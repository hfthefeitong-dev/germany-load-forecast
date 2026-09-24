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

from . import config, evaluate, features, foundation, models, weather
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
                "months": len(mon),
            })
        for a, b in [("ensemble+bc", "ensemble"), ("ensemble+bc", "official+bc"), ("official+bc", "official")]:
            dm = evaluate.diebold_mariano(t, allp[a], allp[b])
            test_rows.append({"window": name, "model": f"DM {a} vs {b}",
                              "test MAPE %": None, "DM_stat": dm["DM_stat"], "p_value": dm["p_value"]})
    return pd.DataFrame(choice_rows), pd.DataFrame(test_rows), monthly
