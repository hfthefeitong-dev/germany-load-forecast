"""Command line entry point.

Run the steps in this order, or all at once with `all`:

    python -m loadfc download   # fetch raw data (a few minutes)
    python -m loadfc run        # features, baselines, LightGBM for every window
    python -m loadfc ablation   # LightGBM without feature groups (main window)
    python -m loadfc chronos    # Chronos-2 zero-shot for every window (GPU)
    python -m loadfc summary    # all tables and figures in reports/
    python -m loadfc all        # run + ablation + chronos + summary

Only `summary` writes to reports/. The earlier steps save intermediate
results to data/processed/, so no step overwrites another step's output.
"""

import json
import sys

import lightgbm as lgb
import pandas as pd

from . import config, cost, evaluate, features, models, plots, rebap, smard, weather

P = config.DATA_PROCESSED


def _pred_path(name: str):
    return P / f"pred_{name}.parquet"


def _meta_path(name: str):
    return P / f"meta_{name}.json"


def _load_meta(name: str) -> dict:
    return json.loads(_meta_path(name).read_text())


def _save_meta(name: str, meta: dict) -> None:
    _meta_path(name).write_text(json.dumps(meta, indent=2))


# ---------------------------------------------------------------------------
def download() -> None:
    config.ensure_dirs()
    start = config.HISTORY_START - pd.Timedelta(days=21)  # room for 2-week lags
    today = pd.Timestamp.now(tz=config.TZ).normalize()

    print("SMARD: load, official forecast, day-ahead price ...")
    smard.download_all(start).to_parquet(config.DATA_RAW / "smard.parquet")

    print("Open-Meteo: 48 h-ahead weather forecasts for 16 states ...")
    weather.download(start, today - pd.Timedelta(days=1)).to_parquet(config.DATA_RAW / "weather.parquet")

    print("netztransparenz: reBAP ...")
    rebap.download(start, today).to_frame().to_parquet(config.DATA_RAW / "rebap.parquet")
    print("done")


def run() -> None:
    """Features, then baselines and LightGBM for every evaluation window."""
    config.ensure_dirs()
    series = pd.read_parquet(config.DATA_RAW / "smard.parquet")
    wx = weather.aggregate(pd.read_parquet(config.DATA_RAW / "weather.parquet"))
    df = features.build(series, wx)
    df = df.join(features.to_ns(pd.read_parquet(config.DATA_RAW / "rebap.parquet")))
    df.to_parquet(P / "features.parquet")

    for name, w in config.WINDOWS.items():
        rounds, valid_mape = models.choose_rounds(df, w)
        print(f"{name}: validation picked {rounds} rounds, MAPE {valid_mape:.2f}%")
        lgbm, last_model = models.rolling_lgbm(df, rounds, w)
        preds = models.baselines(df).loc[lgbm.index].join(lgbm)
        preds.to_parquet(_pred_path(name))
        last_model.save_model(str(P / f"lgbm_{name}.txt"))
        _save_meta(name, {"lgbm_rounds": rounds, "lgbm_valid_MAPE_%": valid_mape})


def ablation() -> None:
    """Which feature groups drive the improvement? Retrain without each group."""
    df = pd.read_parquet(P / "features.parquet")
    w = config.WINDOWS["main"]
    rounds = _load_meta("main")["lgbm_rounds"]
    full = pd.read_parquet(_pred_path("main"))

    groups = {
        "without solar & cloud": ["rad", "rad_south", "rad_daymean", "cloud"],
        "without any weather": ["temp", "cloud", "rad", "rad_south", "temp_daymean", "rad_daymean"],
        "without holiday detail": ["holiday_share", "holiday_share_lag2", "holiday_share_lag7", "bridge", "xmas"],
    }
    cols = {"full model": full["lgbm"], "official": full["official"]}
    for label, drop in groups.items():
        keep = [f for f in features.FEATURES if f not in drop]
        pred, _ = models.rolling_lgbm(df, rounds, w, feature_list=keep)
        cols[label] = pred.loc[full.index]
        print(f"ablation done: {label}")
    pd.DataFrame(cols).to_parquet(P / "ablation_main.parquet")


def chronos() -> None:
    """Chronos-2: choose context length on validation, then forecast the test period."""
    from . import foundation

    df = pd.read_parquet(P / "features.parquet")
    for name, w in config.WINDOWS.items():
        best, scores = foundation.choose_context(df, w)
        print(f"{name}: validation picked context {best} h")
        days = foundation.days_between(df, w.test_start, w.test_end)
        uni = foundation.forecast(df, days, [], best).rename("chronos_uni")
        cov = foundation.forecast(df, days, foundation.COVARIATES, best).rename("chronos_cov")

        preds = pd.read_parquet(_pred_path(name)).drop(columns=["chronos_uni", "chronos_cov"], errors="ignore")
        preds.join(uni).join(cov).to_parquet(_pred_path(name))
        meta = _load_meta(name)
        meta.update({"chronos_context_hours": best, "chronos_valid_MAPE_%": {str(k): v for k, v in scores.items()}})
        _save_meta(name, meta)
        print(f"{name}: chronos done, {len(days)} days")


# ---------------------------------------------------------------------------
def _evaluation_set(df: pd.DataFrame, name: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Test rows where the actual and every model's prediction are known."""
    preds = pd.read_parquet(_pred_path(name))
    preds["ensemble"] = (preds["lgbm"] + preds["chronos_cov"]) / 2
    test = df.loc[preds.index]
    ok = test[features.TARGET].notna() & preds.notna().all(axis=1)
    return test[ok], preds[ok]


def _monthly(test: pd.DataFrame, preds: pd.DataFrame) -> pd.DataFrame:
    y = test[features.TARGET]
    ape = preds.sub(y, axis=0).abs().div(y, axis=0) * 100
    month = test.index.tz_convert(config.TZ).strftime("%Y-%m")
    return ape.groupby(month).mean().rename_axis("month (local time)")


def summary() -> None:
    """All tables and figures. The ensemble is the plain average of LightGBM
    and Chronos-2 with covariates; equal weights involve no tuning, so
    evaluating it on the test period is still fair."""
    config.ensure_dirs()
    df = pd.read_parquet(P / "features.parquet")
    order = ["naive_weekly", "official", "lgbm", "chronos_uni", "chronos_cov", "ensemble"]
    md = ["# Results", "", "Generated by `python -m loadfc summary`. MAPE in %, errors in MW.", ""]
    results = {}
    monthly = {}

    for name, w in config.WINDOWS.items():
        test, preds = _evaluation_set(df, name)
        preds = preds[order]
        meta = _load_meta(name)
        y = test[features.TARGET]
        loc = test.index.tz_convert(config.TZ)

        overall = pd.DataFrame({m: evaluate.metrics(y, preds[m]) for m in preds}).T
        seg = evaluate.segment_table(test, preds)
        dm = pd.DataFrame({
            f"{a} vs {b}": evaluate.diebold_mariano(test, preds[a], preds[b])
            for a, b in [("lgbm", "official"), ("chronos_cov", "official"), ("ensemble", "official"),
                         ("ensemble", "lgbm"), ("lgbm", "chronos_cov")]
        }).T
        mon = _monthly(test, preds)[["official", "lgbm", "chronos_cov", "ensemble"]]
        monthly[name] = mon
        wins = {m: int((mon[m] < mon["official"]).sum()) for m in ["lgbm", "chronos_cov", "ensemble"]}

        md += [
            f"## Window `{name}`: test {loc.min():%Y-%m-%d} to {loc.max():%Y-%m-%d}, {len(test)} hours",
            "",
            f"Validation {w.valid_start:%Y-%m-%d} to {w.test_start - pd.Timedelta(days=1):%Y-%m-%d} picked "
            f"{meta['lgbm_rounds']} LightGBM rounds and a Chronos-2 context of {meta['chronos_context_hours']} h "
            f"(validation MAPE by context: {', '.join(f'{k} h {v:.2f}%' for k, v in meta['chronos_valid_MAPE_%'].items())}).",
            "",
            "### Overall", "", overall.round(2).to_markdown(), "",
            "### MAPE by situation", "", seg.round(2).to_markdown(), "",
            "### Diebold-Mariano tests (daily MAE, Newey-West 7 lags; negative = first model better)", "",
            dm.round(4).to_markdown(), "",
            f"### MAPE by month (months beating the official forecast out of {len(mon)}: "
            + ", ".join(f"{m} {k}" for m, k in wins.items()) + ")", "",
            mon.round(2).to_markdown(), "",
        ]

        ok = test["rebap"].notna()
        if ok.any():
            calm = ok & (test["rebap"].abs() <= 1000)
            costs = cost.cost_table(test[ok], preds[ok])
            costs_calm = cost.cost_table(test[calm], preds[calm])
            md += [
                "### Extra imbalance cost (Germany as one balancing group, a thought experiment)", "",
                costs.round(2).to_markdown(), "",
                f"Excluding the {int((ok & ~calm).sum())} hours with |reBAP| > 1000 EUR/MWh:", "",
                costs_calm.round(2).to_markdown(), "",
            ]
        else:
            costs = None

        results[name] = {
            "test_period": [str(loc.min()), str(loc.max())],
            "hours": len(test),
            **meta,
            "overall": overall.to_dict(orient="index"),
            "months_beating_official": wins,
        }

        if name == "main":
            plots.segment_bars(seg[["official", "lgbm", "chronos_cov", "ensemble"]])
            plots.example_week(test, preds[["official", "lgbm", "chronos_cov"]], "2026-04-20", "04_week_sunny_sunday.png")
            if costs is not None:
                plots.cost_bars(costs.loc[["naive_weekly", "official", "lgbm", "ensemble"]])
            plots.feature_importance(lgb.Booster(model_file=str(P / "lgbm_main.txt")))

    abl_path = P / "ablation_main.parquet"
    if abl_path.exists():
        # Same rows as the main evaluation set, so the numbers are comparable.
        main_index = _evaluation_set(df, "main")[1].index
        abl = pd.read_parquet(abl_path).loc[lambda t: t.index.isin(main_index)]
        test = df.loc[abl.index]
        table = evaluate.segment_table(test, abl)
        md += ["## Ablation, window `main` (LightGBM retrained without each feature group)", "",
               table.round(2).to_markdown(), ""]

    plots.load_patterns(df[df[features.TARGET].notna()])
    plots.official_error_vs_sun(df[df.index.tz_convert(config.TZ) >= config.HISTORY_START])
    plots.monthly_mape(monthly)

    (config.REPORTS / "RESULTS.md").write_text("\n".join(md))
    (config.REPORTS / "results.json").write_text(json.dumps(results, indent=2))
    print("\n".join(md))


def all_steps() -> None:
    run()
    ablation()
    chronos()
    summary()


if __name__ == "__main__":
    commands = {"download": download, "run": run, "ablation": ablation, "chronos": chronos,
                "summary": summary, "all": all_steps}
    if len(sys.argv) != 2 or sys.argv[1] not in commands:
        print(__doc__)
        sys.exit(1)
    commands[sys.argv[1]]()
