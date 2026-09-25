"""Figures for the README."""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from . import config
from .features import TARGET

COLORS = {
    "actual": "#222222",
    "naive_weekly": "#9e9e9e",
    "official": "#d95f02",
    "lgbm": "#1b9e77",
    "chronos_uni": "#b2abd2",
    "chronos_cov": "#7570b3",
    "ensemble": "#e7298a",
}
LABELS = {
    "naive_weekly": "Naive (same hour last week)",
    "official": "Official TSO forecast",
    "lgbm": "LightGBM (this project)",
    "chronos_uni": "Chronos-2, load history only",
    "chronos_cov": "Chronos-2, with covariates",
    "ensemble": "Ensemble (LightGBM + Chronos-2)",
}


def _save(fig, name):
    fig.tight_layout()
    fig.savefig(config.FIGURES / name, dpi=130)
    plt.close(fig)


def monthly_mape(tables: dict[str, pd.DataFrame]) -> None:
    """Month-by-month MAPE across all evaluation windows, in time order."""
    frames = []
    for name, t in tables.items():
        t = t.copy()
        t["window"] = name
        frames.append(t)
    both = pd.concat(frames).sort_index()
    x = pd.to_datetime(both.index)
    fig, ax = plt.subplots(figsize=(11, 4))
    for col in ["official", "lgbm", "chronos_cov", "ensemble"]:
        ax.plot(x, both[col], marker="o", ms=4, lw=1.6, color=COLORS[col], label=LABELS[col])
    for name, t in tables.items():
        start = pd.to_datetime(t.index.min())
        ax.axvline(start, color="#bbb", lw=1, ls=":")
        ax.text(start, ax.get_ylim()[1], f" test window: {name}", va="top", fontsize=8, color="#666")
    ax.set(ylabel="MAPE [%]", title="Month-by-month error in both test windows")
    ax.legend(fontsize=8, loc="upper right")
    _save(fig, "07_monthly_mape.png")


def load_patterns(df: pd.DataFrame) -> None:
    """Daily profiles: working days vs weekends, winter vs summer."""
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    month = df.index.tz_convert(config.TZ).month
    for season, months, ls in [("winter", (12, 1, 2), "-"), ("summer", (6, 7, 8), "--")]:
        m = np.isin(month, months)
        for kind, mask, col in [("working day", df["is_offday"] == 0, "#1b9e77"), ("Sunday / holiday", (df["dow"] == 6) | (df["holiday_share"] >= 0.5), "#d95f02")]:
            prof = df[m & mask].groupby("hour")[TARGET].mean() / 1000
            ax[0].plot(prof.index, prof.values, ls, color=col, label=f"{kind}, {season}")
    ax[0].set(xlabel="hour (local time)", ylabel="load [GW]", title="Average daily profile")
    ax[0].legend(fontsize=8)

    daily = df.groupby("date")[TARGET].mean() / 1000
    ax[1].plot(daily.index, daily.values, lw=0.7, color="#444")
    ax[1].plot(daily.rolling(28, center=True).mean(), color="#d95f02", lw=2, label="28-day mean")
    ax[1].set(ylabel="daily mean load [GW]", title="Seasonality")
    ax[1].legend(fontsize=8)
    _save(fig, "01_load_patterns.png")


def official_error_vs_sun(df: pd.DataFrame) -> None:
    """The finding that motivated the project."""
    midday = df["hour"].between(10, 16) & df[TARGET].notna() & df["load_official"].notna()
    err = (df["load_official"] - df[TARGET]) / df[TARGET] * 100
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for label, mask, col in [("working days", midday & (df["is_offday"] == 0), "#9e9e9e"), ("weekends & holidays", midday & (df["is_offday"] == 1), "#d95f02")]:
        ax.scatter(df.loc[mask, "rad"], err[mask], s=4, alpha=0.35, color=col, label=label)
    ax.axhline(0, color="k", lw=0.8)
    ax.set(xlabel="forecast solar radiation, population-weighted [W/m²]", ylabel="official forecast error [%]\n(positive = over-forecast)", title="Official forecast error at midday (10–16 h) vs sunshine")
    ax.legend(markerscale=4)
    _save(fig, "02_official_error_vs_sun.png")


def segment_bars(table: pd.DataFrame, name: str = "03_mape_by_segment.png") -> None:
    models = [c for c in table.columns if c != "hours"]
    fig, ax = plt.subplots(figsize=(10, 4.5))
    x = np.arange(len(table))
    w = 0.8 / len(models)
    for i, m in enumerate(models):
        ax.bar(x + (i - (len(models) - 1) / 2) * w, table[m], w, label=LABELS.get(m, m), color=COLORS.get(m))
    ax.set_xticks(x, table.index, rotation=20, ha="right")
    ax.set(ylabel="MAPE [%]", title="Test period error by situation (lower is better)")
    ax.legend(fontsize=8)
    _save(fig, name)


def example_week(df: pd.DataFrame, preds: pd.DataFrame, start: str, name: str) -> None:
    a = pd.Timestamp(start, tz=config.TZ)
    m = (df.index >= a) & (df.index < a + pd.Timedelta(days=7))
    loc = df.index[m].tz_convert(config.TZ)
    fig, ax = plt.subplots(figsize=(11, 4))
    ax.plot(loc, df.loc[m, TARGET] / 1000, color=COLORS["actual"], lw=2, label="actual")
    for col in preds.columns:
        ax.plot(loc, preds.loc[m, col] / 1000, color=COLORS.get(col), lw=1.3, label=LABELS.get(col, col))
    ax.set(ylabel="load [GW]", title=f"Week of {start}")
    ax.legend(fontsize=8)
    _save(fig, name)


def cost_bars(table: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar([LABELS.get(i, i) for i in table.index], table["extra_cost_mEUR"], color=[COLORS.get(i) for i in table.index])
    ax.set(ylabel="extra imbalance cost [million EUR]", title="Cost of forecast errors in the test period")
    plt.setp(ax.get_xticklabels(), rotation=15, ha="right")
    _save(fig, "05_imbalance_cost.png")


def feature_importance(model) -> None:
    imp = pd.Series(model.feature_importance("gain"), index=model.feature_name()).sort_values()
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.barh(imp.index, imp.values / imp.sum() * 100, color="#1b9e77")
    ax.set(xlabel="share of total gain [%]", title="LightGBM feature importance")
    _save(fig, "06_feature_importance.png")


def fan_chart(test: pd.DataFrame, q: pd.DataFrame, official: pd.Series, method: str, start: str) -> None:
    """Probabilistic forecast for one week: median, 80 % and 90 % bands, actual, official."""
    a = pd.Timestamp(start, tz=config.TZ)
    m = (q.index >= a) & (q.index < a + pd.Timedelta(days=7))
    loc = q.index[m].tz_convert(config.TZ)
    qq = q[m] / 1000
    fig, ax = plt.subplots(figsize=(11, 4))
    ax.fill_between(loc, qq[0.05], qq[0.95], color="#1b9e77", alpha=0.18, label="90 % interval")
    ax.fill_between(loc, qq[0.1], qq[0.9], color="#1b9e77", alpha=0.30, label="80 % interval")
    ax.plot(loc, qq[0.5], color="#1b9e77", lw=1.4, label=f"median: {method}")
    ax.plot(loc, test.loc[m, TARGET] / 1000, color=COLORS["actual"], lw=2, label="actual")
    ax.plot(loc, official[m] / 1000, color=COLORS["official"], lw=1.3, label="official forecast")
    ax.set(ylabel="load [GW]", title=f"Probabilistic forecast, week of {start}")
    ax.legend(fontsize=8, ncol=2)
    _save(fig, "08_probabilistic_week.png")
