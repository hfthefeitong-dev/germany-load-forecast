"""Command line entry point.

    python -m loadfc download   # fetch all raw data (a few minutes)
    python -m loadfc run        # features, models, evaluation, figures
"""

import json
import sys

import pandas as pd

from . import config, cost, evaluate, features, models, plots, rebap, smard, weather


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
    config.ensure_dirs()
    series = pd.read_parquet(config.DATA_RAW / "smard.parquet")
    wx = weather.aggregate(pd.read_parquet(config.DATA_RAW / "weather.parquet"))
    df = features.build(series, wx)
    df = df.join(features.to_ns(pd.read_parquet(config.DATA_RAW / "rebap.parquet")))
    df.to_parquet(config.DATA_PROCESSED / "features.parquet")

    rounds, valid_mape = models.choose_rounds(df)
    print(f"validation: {rounds} rounds, MAPE {valid_mape:.2f}%")

    lgbm, last_model = models.rolling_lgbm(df, rounds)
    preds = models.baselines(df).join(lgbm)

    # Evaluate only where every model has a prediction and the actual is known.
    test = df.loc[lgbm.index]
    preds = preds.loc[lgbm.index]
    ok = test[features.TARGET].notna() & preds.notna().all(axis=1)
    test, preds = test[ok], preds[ok]
    preds.to_parquet(config.DATA_PROCESSED / "predictions.parquet")

    overall = {m: evaluate.metrics(test[features.TARGET], preds[m]) for m in preds}
    seg = evaluate.segment_table(test, preds)
    dm = evaluate.diebold_mariano(test, preds["lgbm"], preds["official"])
    costs = cost.cost_table(test, preds)

    loc = test.index.tz_convert(config.TZ)
    results = {
        "test_period": [str(loc.min()), str(loc.max())],
        "validation": {"rounds": rounds, "MAPE_%": valid_mape},
        "overall": overall,
        "diebold_mariano_lgbm_vs_official": dm,
    }
    (config.REPORTS / "results.json").write_text(json.dumps(results, indent=2))
    (config.REPORTS / "segments.md").write_text(seg.round(2).to_markdown() if _has_tabulate() else seg.round(2).to_string())
    (config.REPORTS / "costs.md").write_text(costs.round(2).to_markdown() if _has_tabulate() else costs.round(2).to_string())

    plots.load_patterns(df[df[features.TARGET].notna()])
    plots.official_error_vs_sun(df[df.index.tz_convert(config.TZ) >= config.HISTORY_START])
    plots.segment_bars(seg.drop(columns="hours"))
    plots.example_week(test, preds, "2026-04-20", "04_week_sunny_sunday.png")
    plots.cost_bars(costs)
    plots.feature_importance(last_model)

    print(json.dumps(results, indent=2))
    print(seg.round(2).to_string())
    print(costs.round(2).to_string())


def ablation() -> None:
    """Which feature groups drive the improvement? Retrain without each group."""
    df = pd.read_parquet(config.DATA_PROCESSED / "features.parquet")
    results = json.loads((config.REPORTS / "results.json").read_text())
    rounds = results["validation"]["rounds"]
    full = pd.read_parquet(config.DATA_PROCESSED / "predictions.parquet")

    groups = {
        "without solar & cloud": ["rad", "rad_south", "rad_daymean", "cloud"],
        "without any weather": ["temp", "cloud", "rad", "rad_south", "temp_daymean", "rad_daymean"],
        "without holiday detail": ["holiday_share", "holiday_share_lag2", "holiday_share_lag7", "bridge", "xmas"],
    }
    test = df.loc[full.index]
    cols = {"full model": full["lgbm"], "official": full["official"]}
    for name, drop in groups.items():
        keep = [f for f in features.FEATURES if f not in drop]
        pred, _ = models.rolling_lgbm(df, rounds, feature_list=keep)
        cols[name] = pred.loc[full.index]
        print(f"done: {name}")
    table = evaluate.segment_table(test, pd.DataFrame(cols))
    (config.REPORTS / "ablation.md").write_text(table.round(2).to_markdown())
    print(table.round(2).to_string())

    # Robustness of the cost result to extreme imbalance prices.
    ok = test["rebap"].abs() <= 1000
    robust = cost.cost_table(test[ok], full[ok][["naive_weekly", "official", "lgbm"]])
    (config.REPORTS / "costs_without_price_spikes.md").write_text(robust.round(2).to_markdown())
    print("\ncost, hours with |reBAP| <= 1000 EUR/MWh only:")
    print(robust.round(2).to_string())


def chronos() -> None:
    """Zero-shot Chronos-2, with and without covariates, on the same test days."""
    from . import foundation

    df = pd.read_parquet(config.DATA_PROCESSED / "features.parquet")
    base = pd.read_parquet(config.DATA_PROCESSED / "predictions.parquet")
    days = foundation.test_days(df)

    uni = foundation.forecast(df, days, covariates=[]).rename("chronos_uni")
    cov = foundation.forecast(df, days, covariates=foundation.COVARIATES).rename("chronos_cov")
    preds = base.join(uni).join(cov)
    preds = preds[preds.notna().all(axis=1)]
    preds.to_parquet(config.DATA_PROCESSED / "predictions_with_chronos.parquet")

    test = df.loc[preds.index]
    overall = pd.DataFrame({m: evaluate.metrics(test[features.TARGET], preds[m]) for m in preds}).T
    seg = evaluate.segment_table(test, preds)
    dm = evaluate.diebold_mariano(test, preds["lgbm"], preds["chronos_cov"])
    text = (
        "## Overall\n\n" + overall.round(2).to_markdown()
        + "\n\n## MAPE by situation [%]\n\n" + seg.round(2).to_markdown()
        + f"\n\n## Diebold-Mariano, LightGBM vs Chronos-2 with covariates\n\n{json.dumps(dm, indent=2)}\n"
    )
    (config.REPORTS / "foundation.md").write_text(text)
    plots.segment_bars(seg.drop(columns="hours")[["official", "lgbm", "chronos_uni", "chronos_cov"]], name="07_mape_with_chronos.png")
    print(text)


def summary() -> None:
    """Final tables and figures for the README, including a simple ensemble.

    The ensemble is the plain average of LightGBM and Chronos-2 with
    covariates. Equal weights involve no tuning, so evaluating it on the
    test period is still fair.
    """
    df = pd.read_parquet(config.DATA_PROCESSED / "features.parquet")
    preds = pd.read_parquet(config.DATA_PROCESSED / "predictions_with_chronos.parquet")
    preds["ensemble"] = (preds["lgbm"] + preds["chronos_cov"]) / 2
    test = df.loc[preds.index]
    y = test[features.TARGET]

    overall = pd.DataFrame({m: evaluate.metrics(y, preds[m]) for m in preds}).T
    seg = evaluate.segment_table(test, preds)
    dm = {
        f"{a} vs {b}": evaluate.diebold_mariano(test, preds[a], preds[b])
        for a, b in [("lgbm", "official"), ("chronos_cov", "official"), ("ensemble", "official"), ("ensemble", "lgbm")]
    }
    ok = test["rebap"].notna()
    costs = cost.cost_table(test[ok], preds[ok])
    spikes = test["rebap"].abs() <= 1000
    costs_robust = cost.cost_table(test[ok & spikes], preds[ok & spikes])

    md = [
        "# Results\n",
        f"Test period: {test.index.tz_convert(config.TZ).min():%Y-%m-%d} to {test.index.tz_convert(config.TZ).max():%Y-%m-%d}, {len(test)} hours.\n",
        "## Overall\n", overall.round(2).to_markdown(), "",
        "## MAPE by situation [%]\n", seg.round(2).to_markdown(), "",
        "## Diebold-Mariano tests (daily MAE, Newey-West, 7 lags; negative = first model better)\n",
        pd.DataFrame(dm).T.round(4).to_markdown(), "",
        "## Extra imbalance cost (whole of Germany as one balancing group, a thought experiment)\n",
        costs.round(2).to_markdown(), "",
        "### Same, excluding hours with |reBAP| > 1000 EUR/MWh\n",
        costs_robust.round(2).to_markdown(), "",
    ]
    (config.REPORTS / "RESULTS.md").write_text("\n".join(md))

    plots.segment_bars(seg[["official", "lgbm", "chronos_cov", "ensemble"]], name="03_mape_by_segment.png")
    plots.cost_bars(costs.loc[["naive_weekly", "official", "lgbm", "ensemble"]])
    plots.example_week(test, preds[["official", "lgbm", "chronos_cov"]], "2026-04-20", "04_week_sunny_sunday.png")
    print("\n".join(md))


def _has_tabulate() -> bool:
    try:
        import tabulate  # noqa: F401
        return True
    except ImportError:
        return False


if __name__ == "__main__":
    commands = {"download": download, "run": run, "ablation": ablation, "chronos": chronos, "summary": summary}
    commands[sys.argv[1]]()
