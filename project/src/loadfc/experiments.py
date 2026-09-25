"""Exploration experiments, kept separate from the frozen main pipeline.

Rule: every decision here is made on the validation periods. The test
periods are looked at once, after all parameters are fixed.

1. upper_bound      How much accuracy is lost because the inputs are
                    imperfect? Retrain LightGBM with information a real
                    forecaster cannot have and measure the gain.
2. bias_correction  Errors persist for weeks. Correct each forecast by the
                    recent average error, using only errors that are known
                    at forecast time (up to day D-2).
"""

import itertools
import json

import lightgbm as lgb
import pandas as pd

from . import capacity, config, evaluate, features, foundation, models, weather
from .features import FEATURES, TARGET

P = config.DATA_PROCESSED


def _mape(pred: pd.Series, y: pd.Series) -> float:
    ok = pred.notna() & y.notna()
    return float(((pred[ok] - y[ok]).abs() / y[ok]).mean() * 100)


# ============================================================ 1. upper bound
FRESH_LOAD = ["load_lag24", "load_daymean_lag1"]


def _add_fresh_load(df: pd.DataFrame) -> pd.DataFrame:
    """Load from day D-1. Not available when the forecast is made: cheating on purpose."""
    df = df.copy()
    df["load_lag24"] = df[TARGET].shift(24)
    daily = df[TARGET].groupby(df["date"]).mean()
    df["load_daymean_lag1"] = (df["date"] - pd.Timedelta(days=1)).map(daily)
    return df


def _fit_on_validation(df: pd.DataFrame, w: config.Window, feats: list[str]) -> tuple[float, int]:
    """Train before the validation period, early-stop on it, return (MAPE, trees).

    Early stopping on the evaluation data is slightly optimistic, but equally
    so for every variant, which is what matters for a comparison.
    """
    loc = df.index.tz_convert(config.TZ)
    train = models._trainable(df[(loc >= config.HISTORY_START) & (loc < w.valid_start - pd.Timedelta(days=1))])
    valid = models._trainable(df[(loc >= w.valid_start) & (loc < w.test_start)])
    model = lgb.train(
        models.PARAMS,
        lgb.Dataset(train[feats], train[TARGET]),
        num_boost_round=5000,
        valid_sets=[lgb.Dataset(valid[feats], valid[TARGET])],
        callbacks=[lgb.early_stopping(200, verbose=False)],
    )
    pred = pd.Series(model.predict(valid[feats], num_iteration=model.best_iteration), index=valid.index)
    return _mape(pred, valid[TARGET]), model.best_iteration


def upper_bound() -> pd.DataFrame:
    series = pd.read_parquet(config.DATA_RAW / "smard.parquet")
    obs_path = config.DATA_RAW / "weather_observed.parquet"
    if not obs_path.exists():
        # Download observed weather only up to the end of the last validation
        # period, so it can never touch a test period.
        start = config.HISTORY_START - pd.Timedelta(days=21)
        end = config.WINDOWS["main"].test_start - pd.Timedelta(days=1)
        print("Open-Meteo archive: observed weather (ERA5) ...")
        weather.download_observed(start, end).to_parquet(obs_path)

    df_fc = _add_fresh_load(pd.read_parquet(P / "features.parquet"))
    df_obs = _add_fresh_load(features.build(series, weather.aggregate(pd.read_parquet(obs_path))))

    variants = [
        ("current: 48 h-ahead weather forecast, load up to D-2", df_fc, FEATURES),
        ("cheat: observed weather", df_obs, FEATURES),
        ("cheat: load of the full day D-1", df_fc, FEATURES + FRESH_LOAD),
        ("cheat: both", df_obs, FEATURES + FRESH_LOAD),
    ]
    rows = []
    for name, w in config.WINDOWS.items():
        loc = df_fc.index.tz_convert(config.TZ)
        v = df_fc[(loc >= w.valid_start) & (loc < w.test_start)]
        rows.append({"window": name, "variant": "official forecast (reference)",
                     "validation MAPE %": _mape(v["load_official"], v[TARGET]), "trees": None})
        for label, d, feats in variants:
            mape, trees = _fit_on_validation(d, w, feats)
            rows.append({"window": name, "variant": label, "validation MAPE %": mape, "trees": trees})
            print(f"{name:8s} {label:55s} {mape:.2f}%")
    return pd.DataFrame(rows)


# ========================================================= 2. bias correction
GRID = {
    "window_days": [1, 2, 3, 5, 7, 14],
    "alpha": [0.25, 0.5, 0.75, 1.0],
    "by_hour": [False, True],
}


def correct(pred: pd.Series, actual: pd.Series, date: pd.Series, hour: pd.Series,
            window_days: int, alpha: float, by_hour: bool) -> pd.Series:
    """Subtract `alpha` times the mean error of the last `window_days` known days.

    The forecast for day D is made on D-1, when actuals are known up to the
    end of D-2. `shift(2)` on a gap-free daily index enforces exactly that.
    With `by_hour`, the correction is computed separately for each hour of
    the day; otherwise one number per day.
    """
    err = pred - actual
    days = pd.date_range(date.min(), date.max(), freq="D")
    if by_hour:
        e = err.groupby([date, hour]).mean().unstack().reindex(days)
        c = e.shift(2).rolling(window_days, min_periods=1).mean()
        lookup = c.stack()
        corr = pd.Series(list(zip(date, hour)), index=pred.index).map(lookup)
    else:
        e = err.groupby(date).mean().reindex(days)
        c = e.shift(2).rolling(window_days, min_periods=1).mean()
        corr = date.map(c)
    return pred - alpha * corr.fillna(0).astype("float64")


def _validation_forecasts(df: pd.DataFrame, name: str, w: config.Window) -> pd.DataFrame:
    """Genuine out-of-sample forecasts for the validation period, cached."""
    path = P / f"valid_pred_{name}.parquet"
    if path.exists():
        return pd.read_parquet(path)
    meta = json.loads((P / f"meta_{name}.json").read_text())
    as_test = config.Window(f"{name}-valid", w.valid_start, w.valid_start, w.test_start)
    lg, _ = models.rolling_lgbm(df, meta["lgbm_rounds"], as_test)
    days = foundation.days_between(df, w.valid_start, w.test_start)
    ch = foundation.forecast(df, days, foundation.COVARIATES, meta["chronos_context_hours"])
    out = pd.DataFrame({"lgbm": lg}).join(ch.rename("chronos_cov"), how="inner")
    out["official"] = df.loc[out.index, "load_official"]
    out["ensemble"] = (out["lgbm"] + out["chronos_cov"]) / 2
    out.to_parquet(path)
    return out


def _choose(df: pd.DataFrame, valid: pd.DataFrame, model: str) -> tuple[dict, float, float]:
    """Best correction parameters on validation. Returns (params, MAPE before, MAPE after)."""
    d = df.loc[valid.index]
    local = valid.index.tz_convert(config.TZ)
    date = pd.Series(d["date"].to_numpy(), index=valid.index)
    hour = pd.Series(local.hour, index=valid.index)
    y = d[TARGET]
    best, best_mape = None, float("inf")
    for wd, a, bh in itertools.product(*GRID.values()):
        m = _mape(correct(valid[model], y, date, hour, wd, a, bh), y)
        if m < best_mape:
            best, best_mape = {"window_days": wd, "alpha": a, "by_hour": bh}, m
    return best, _mape(valid[model], y), best_mape


def bias_correction() -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    df = pd.read_parquet(P / "features.parquet")
    choice_rows, test_rows, monthly = [], [], {}
    for name, w in config.WINDOWS.items():
        valid = _validation_forecasts(df, name, w)
        test = pd.read_parquet(P / f"pred_{name}.parquet")
        test["ensemble"] = (test["lgbm"] + test["chronos_cov"]) / 2
        test = test[["lgbm", "chronos_cov", "official", "ensemble"]].dropna()

        # Validation and test forecasts form one continuous history, so the
        # first test days can use the errors of the last validation days.
        both = pd.concat([valid[test.columns], test]).sort_index()
        both = both[~both.index.duplicated(keep="last")]
        d = df.loc[both.index]
        date = pd.Series(d["date"].to_numpy(), index=both.index)
        hour = pd.Series(both.index.tz_convert(config.TZ).hour, index=both.index)

        corrected = pd.DataFrame(index=test.index)
        for model in ["lgbm", "chronos_cov", "ensemble", "official"]:
            params, before, after = _choose(df, valid, model)
            choice_rows.append({"window": name, "model": model, **params,
                                "valid MAPE before %": before, "valid MAPE after %": after})
            full = correct(both[model], d[TARGET], date, hour, **params)
            corrected[f"{model}+bc"] = full.loc[test.index]
            print(f"{name:8s} {model:12s} picked {params}: validation {before:.2f}% -> {after:.2f}%")

        t = df.loc[test.index]
        y = t[TARGET]
        allp = test.join(corrected)
        mon = (allp.sub(y, axis=0).abs().div(y, axis=0) * 100).groupby(
            t.index.tz_convert(config.TZ).strftime("%Y-%m")).mean()
        monthly[name] = mon
        for col in allp:
            test_rows.append({
                "window": name, "model": col, "test MAPE %": _mape(allp[col], y),
                "months beating official": int((mon[col] < mon["official"]).sum()),
                "months beating official+bc": int((mon[col] < mon["official+bc"]).sum()),
                "months": len(mon),
            })
        for a, b in [("ensemble+bc", "ensemble"), ("ensemble+bc", "official+bc"), ("official+bc", "official")]:
            dm = evaluate.diebold_mariano(t, allp[a], allp[b])
            test_rows.append({"window": name, "model": f"DM {a} vs {b}",
                              "test MAPE %": None, "DM_stat": dm["DM_stat"], "p_value": dm["p_value"]})
    return pd.DataFrame(choice_rows), pd.DataFrame(test_rows), monthly


# ======================================================= 3. morning load of D-1
# Pre-registered decision rule, fixed before looking at any test result:
# the morning features count as an improvement only if they lower the
# validation MAPE in BOTH windows, for LightGBM and for Chronos-2.


def _official_bc(df: pd.DataFrame, name: str, w: config.Window, test_index: pd.Index) -> pd.Series:
    """The stronger benchmark: official forecast with validation-tuned bias correction."""
    valid = _validation_forecasts(df, name, w)
    params, _, _ = _choose(df, valid, "official")
    both = pd.concat([valid["official"], df.loc[test_index, "load_official"]]).sort_index()
    both = both[~both.index.duplicated(keep="last")]
    d = df.loc[both.index]
    date = pd.Series(d["date"].to_numpy(), index=both.index)
    hour = pd.Series(both.index.tz_convert(config.TZ).hour, index=both.index)
    return correct(both, d[TARGET], date, hour, **params).loc[test_index]


def morning_load() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df = pd.read_parquet(P / "features.parquet")
    dfm = features.add_morning_load(df)
    feats_m = FEATURES + features.MORNING_FEATURES
    valid_rows, test_rows, seg = [], [], None

    for name, w in config.WINDOWS.items():
        ctx = json.loads((P / f"meta_{name}.json").read_text())["chronos_context_hours"]

        # ---- validation: the decision
        lg_before, _ = _fit_on_validation(dfm, w, FEATURES)
        lg_after, _ = _fit_on_validation(dfm, w, feats_m)
        vdays = foundation.days_between(df, w.valid_start, w.test_start)
        c0 = foundation.forecast(df, vdays, foundation.COVARIATES, ctx, cut_hour=0)
        c8 = foundation.forecast(df, vdays, foundation.COVARIATES, ctx, cut_hour=features.MORNING_UNTIL)
        ch_before, ch_after = _mape(c0, df.loc[c0.index, TARGET]), _mape(c8, df.loc[c8.index, TARGET])
        valid_rows += [
            {"window": name, "model": "LightGBM", "valid MAPE, load up to D-2 %": lg_before,
             "valid MAPE, + D-1 until 08:00 %": lg_after},
            {"window": name, "model": "Chronos-2", "valid MAPE, load up to D-2 %": ch_before,
             "valid MAPE, + D-1 until 08:00 %": ch_after},
        ]
        print(f"{name:8s} validation  LightGBM {lg_before:.2f}% -> {lg_after:.2f}%   Chronos-2 {ch_before:.2f}% -> {ch_after:.2f}%")

        # ---- test: looked at once, everything frozen
        rounds, _ = models.choose_rounds(dfm, w, feature_list=feats_m)
        lg_m, _ = models.rolling_lgbm(dfm, rounds, w, feature_list=feats_m)
        tdays = foundation.days_between(df, w.test_start, w.test_end)
        ch_m = foundation.forecast(df, tdays, foundation.COVARIATES, ctx, cut_hour=features.MORNING_UNTIL)

        base = pd.read_parquet(P / f"pred_{name}.parquet")
        base["ensemble"] = (base["lgbm"] + base["chronos_cov"]) / 2
        preds = base[["official", "ensemble"]].join(lg_m.rename("lgbm_morning")).join(
            ch_m.rename("chronos_morning")).dropna()
        preds["ensemble_morning"] = (preds["lgbm_morning"] + preds["chronos_morning"]) / 2
        preds["official+bc"] = _official_bc(df, name, w, preds.index)
        preds.to_parquet(P / f"morning_pred_{name}.parquet")  # reused by the fine-tuning experiment
        preds = preds[["official", "official+bc", "ensemble", "lgbm_morning", "chronos_morning", "ensemble_morning"]]

        t = df.loc[preds.index]
        y = t[TARGET]
        mon = (preds.sub(y, axis=0).abs().div(y, axis=0) * 100).groupby(
            t.index.tz_convert(config.TZ).strftime("%Y-%m")).mean()
        for col in preds:
            test_rows.append({
                "window": name, "model": col, "test MAPE %": _mape(preds[col], y),
                "months beating official": int((mon[col] < mon["official"]).sum()),
                "months beating official+bc": int((mon[col] < mon["official+bc"]).sum()),
                "months": len(mon),
            })
        for a, b in [("ensemble_morning", "ensemble"), ("ensemble_morning", "official+bc")]:
            dm = evaluate.diebold_mariano(t, preds[a], preds[b])
            test_rows.append({"window": name, "model": f"DM {a} vs {b}",
                              "DM_stat": dm["DM_stat"], "p_value": dm["p_value"]})
        if name == "main":
            seg = evaluate.segment_table(t, preds)
    return pd.DataFrame(valid_rows), pd.DataFrame(test_rows), seg


# ================================================== 4. fine-tuning Chronos-2
# Pre-registered decision rule: fine-tuning counts as an improvement only if
# the best fine-tuned configuration beats zero-shot Chronos-2 on the
# validation period of BOTH windows.
#
# Protocol per window:
#   selection  fine-tune on data up to one day before the validation period,
#              score each configuration with the usual day-ahead procedure
#   test       fine-tune once more with the chosen configuration on all data
#              up to one day before the test period, then forecast the whole
#              test period with that model (no monthly refresh)

FT_CONFIGS = [
    {"finetune_mode": "lora", "learning_rate": 1e-5, "num_steps": 500},
    {"finetune_mode": "lora", "learning_rate": 1e-5, "num_steps": 2000},
    {"finetune_mode": "full", "learning_rate": 1e-6, "num_steps": 500},
    {"finetune_mode": "full", "learning_rate": 1e-6, "num_steps": 2000},
]
FT_CONTEXT = 2048   # fine-tuning with 8192 h is ~10x slower (2.7 s per step)
FT_BATCH = 64


def _finetune(df: pd.DataFrame, until: pd.Timestamp, cfg: dict):
    """Fine-tune a copy of Chronos-2 on the load history before `until`."""
    import shutil

    import torch
    from chronos.chronos2 import preprocess

    tr = df[(df.index >= config.HISTORY_START.tz_convert("UTC")) & (df.index < until.tz_convert("UTC"))]
    long = tr[[TARGET, *foundation.COVARIATES]].copy()
    long["id"], long["timestamp"] = "DE", long.index.tz_localize(None)
    inputs = preprocess.from_data_frame(
        long.reset_index(drop=True), target_columns=[TARGET], prediction_length=foundation.HORIZON,
        known_covariates_names=foundation.COVARIATES, id_column="id", timestamp_column="timestamp",
    )
    out = config.ROOT / "data" / "chronos_ft_tmp"
    torch.manual_seed(0)
    ft = foundation._pipeline().fit(
        inputs, prediction_length=foundation.HORIZON, context_length=FT_CONTEXT, batch_size=FT_BATCH,
        output_dir=str(out), report_to="none", seed=0, **cfg,
    )
    shutil.rmtree(out, ignore_errors=True)  # intermediate checkpoints are ~0.5 GB each
    return ft


def finetune() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    import gc

    import torch

    df = pd.read_parquet(P / "features.parquet")
    select_rows, test_rows, seg = [], [], None
    for name, w in config.WINDOWS.items():
        meta = json.loads((P / f"meta_{name}.json").read_text())
        zero_shot = min(meta["chronos_valid_MAPE_%"].values())
        vdays = foundation.days_between(df, w.valid_start, w.test_start)

        # ---- selection on validation
        best = None
        for cfg in FT_CONFIGS:
            ft = _finetune(df, w.valid_start - pd.Timedelta(days=1), cfg)
            for ctx in foundation.CONTEXT_OPTIONS:
                pred = foundation.forecast(df, vdays, foundation.COVARIATES, ctx, pipe=ft)
                mape = _mape(pred, df.loc[pred.index, TARGET])
                select_rows.append({"window": name, **cfg, "inference context h": ctx,
                                    "valid MAPE %": mape, "zero-shot valid MAPE %": zero_shot})
                print(f"{name:8s} {cfg} ctx {ctx}: {mape:.2f}% (zero-shot {zero_shot:.2f}%)", flush=True)
                if best is None or mape < best[0]:
                    best = (mape, cfg, ctx)
            del ft
            gc.collect()
            torch.cuda.empty_cache()

        # ---- test, once, with the chosen configuration
        _, cfg, ctx = best
        print(f"{name:8s} chosen {cfg}, inference context {ctx} h", flush=True)
        ft = _finetune(df, w.test_start - pd.Timedelta(days=1), cfg)
        tdays = foundation.days_between(df, w.test_start, w.test_end)
        ch_ft = foundation.forecast(df, tdays, foundation.COVARIATES, ctx, pipe=ft).rename("chronos_ft")
        ch_ft_m = foundation.forecast(df, tdays, foundation.COVARIATES, ctx, pipe=ft,
                                      cut_hour=features.MORNING_UNTIL).rename("chronos_ft_morning")
        del ft
        gc.collect()
        torch.cuda.empty_cache()

        base = pd.read_parquet(P / f"pred_{name}.parquet")
        base["ensemble"] = (base["lgbm"] + base["chronos_cov"]) / 2
        morning = pd.read_parquet(P / f"morning_pred_{name}.parquet")
        preds = (base[["official", "chronos_cov", "lgbm", "ensemble"]]
                 .join(morning[["official+bc", "lgbm_morning", "ensemble_morning"]])
                 .join(ch_ft).join(ch_ft_m).dropna())
        preds["ensemble_ft"] = (preds["lgbm"] + preds["chronos_ft"]) / 2
        preds["ensemble_ft_morning"] = (preds["lgbm_morning"] + preds["chronos_ft_morning"]) / 2
        preds = preds[["official", "official+bc", "chronos_cov", "chronos_ft", "ensemble", "ensemble_ft",
                       "ensemble_morning", "ensemble_ft_morning"]]
        preds.to_parquet(P / f"finetune_pred_{name}.parquet")

        t = df.loc[preds.index]
        y = t[TARGET]
        mon = (preds.sub(y, axis=0).abs().div(y, axis=0) * 100).groupby(
            t.index.tz_convert(config.TZ).strftime("%Y-%m")).mean()
        for col in preds:
            test_rows.append({
                "window": name, "model": col, "test MAPE %": _mape(preds[col], y),
                "months beating official": int((mon[col] < mon["official"]).sum()),
                "months beating official+bc": int((mon[col] < mon["official+bc"]).sum()),
                "months": len(mon),
            })
        for a, b in [("chronos_ft", "chronos_cov"), ("ensemble_ft", "ensemble"),
                     ("ensemble_ft_morning", "ensemble_morning"), ("ensemble_ft_morning", "official+bc")]:
            dm = evaluate.diebold_mariano(t, preds[a], preds[b])
            test_rows.append({"window": name, "model": f"DM {a} vs {b}",
                              "DM_stat": dm["DM_stat"], "p_value": dm["p_value"]})
        test_rows.append({"window": name, "model": f"chosen: {cfg}, inference context {ctx} h"})
        if name == "main":
            seg = evaluate.segment_table(t, preds)
    return pd.DataFrame(select_rows), pd.DataFrame(test_rows), seg



# ============================================ 5. PV and battery capacity
# Pre-registered decision rule, per model: the capacity features count as an
# improvement only if they lower the validation MAPE in BOTH windows.

PV_COVARIATES = ["pv_potential", "pv_potential_south", "battery_evening"]


def _pv_slope_by_year(df: pd.DataFrame) -> pd.DataFrame:
    """Diagnostic: how strongly does the official forecast's midday error grow with sunshine, per year?

    Slope of a least-squares line through (radiation, official error in %),
    for working-day and off-day middays separately. A slope that rises over
    the years means the official forecast falls further behind the PV build-out.
    """
    loc = df.index.tz_convert(config.TZ)
    mid = df["hour"].between(10, 16) & df[TARGET].notna() & df["load_official"].notna() & df["rad"].notna()
    err = (df["load_official"] - df[TARGET]) / df[TARGET] * 100
    rows = []
    for year in sorted(set(loc.year)):
        for label, mask in [("working days", df["is_offday"] == 0), ("weekends & holidays", df["is_offday"] == 1)]:
            m = mid & mask & (loc.year == year)
            if m.sum() < 200:
                continue
            x, y = df.loc[m, "rad"], err[m]
            slope = float(((x - x.mean()) * (y - y.mean())).sum() / ((x - x.mean()) ** 2).sum())
            rows.append({"year": year, "days": label, "hours": int(m.sum()),
                         "error slope, % per 100 W/m2": slope * 100})
    return pd.DataFrame(rows)


def pv_capacity() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df = pd.read_parquet(P / "features.parquet")
    cap = capacity.load()
    dfp = features.add_pv_features(df, cap)
    feats_pv = FEATURES + features.PV_FEATURES
    cov_pv = foundation.COVARIATES + PV_COVARIATES

    valid_rows, test_rows, seg = [], [], None
    for name, w in config.WINDOWS.items():
        ctx = json.loads((P / f"meta_{name}.json").read_text())["chronos_context_hours"]

        # ---- validation: the decision
        lg_before, _ = _fit_on_validation(dfp, w, FEATURES)
        lg_after, _ = _fit_on_validation(dfp, w, feats_pv)
        vdays = foundation.days_between(df, w.valid_start, w.test_start)
        c0 = foundation.forecast(dfp, vdays, foundation.COVARIATES, ctx)
        c1 = foundation.forecast(dfp, vdays, cov_pv, ctx)
        ch_before, ch_after = _mape(c0, dfp.loc[c0.index, TARGET]), _mape(c1, dfp.loc[c1.index, TARGET])
        valid_rows += [
            {"window": name, "model": "LightGBM", "valid MAPE before %": lg_before, "valid MAPE with PV features %": lg_after},
            {"window": name, "model": "Chronos-2", "valid MAPE before %": ch_before, "valid MAPE with PV features %": ch_after},
        ]
        print(f"{name:8s} validation  LightGBM {lg_before:.2f}% -> {lg_after:.2f}%   "
              f"Chronos-2 {ch_before:.2f}% -> {ch_after:.2f}%", flush=True)

        # ---- test: looked at once
        rounds, _ = models.choose_rounds(dfp, w, feature_list=feats_pv)
        lg_pv, last_model = models.rolling_lgbm(dfp, rounds, w, feature_list=feats_pv)
        tdays = foundation.days_between(df, w.test_start, w.test_end)
        ch_pv = foundation.forecast(dfp, tdays, cov_pv, ctx)

        base = pd.read_parquet(P / f"pred_{name}.parquet")
        base["ensemble"] = (base["lgbm"] + base["chronos_cov"]) / 2
        morning = pd.read_parquet(P / f"morning_pred_{name}.parquet")
        preds = (base[["official", "lgbm", "chronos_cov", "ensemble"]].join(morning[["official+bc"]])
                 .join(lg_pv.rename("lgbm_pv")).join(ch_pv.rename("chronos_pv")).dropna())
        preds["ensemble_pv"] = (preds["lgbm_pv"] + preds["chronos_pv"]) / 2
        preds = preds[["official", "official+bc", "lgbm", "lgbm_pv", "chronos_cov", "chronos_pv", "ensemble", "ensemble_pv"]]
        preds.to_parquet(P / f"pv_pred_{name}.parquet")

        t = dfp.loc[preds.index]
        y = t[TARGET]
        mon = (preds.sub(y, axis=0).abs().div(y, axis=0) * 100).groupby(
            t.index.tz_convert(config.TZ).strftime("%Y-%m")).mean()
        for col in preds:
            test_rows.append({
                "window": name, "model": col, "test MAPE %": _mape(preds[col], y),
                "months beating official": int((mon[col] < mon["official"]).sum()),
                "months beating official+bc": int((mon[col] < mon["official+bc"]).sum()),
                "months": len(mon),
            })
        for a, b in [("lgbm_pv", "lgbm"), ("chronos_pv", "chronos_cov"), ("ensemble_pv", "ensemble")]:
            dm = evaluate.diebold_mariano(t, preds[a], preds[b])
            test_rows.append({"window": name, "model": f"DM {a} vs {b}", "DM_stat": dm["DM_stat"], "p_value": dm["p_value"]})
        if name == "main":
            seg = evaluate.segment_table(t, preds)
            imp = pd.Series(last_model.feature_importance("gain"), index=last_model.feature_name())
            importance = (imp / imp.sum() * 100).sort_values(ascending=False).rename("share of gain %").to_frame()

    diag = _pv_slope_by_year(df)
    return diag, pd.DataFrame(valid_rows), pd.DataFrame(test_rows), seg, importance
