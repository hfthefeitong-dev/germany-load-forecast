"""Error metrics, segment analysis and a significance test."""

import numpy as np
import pandas as pd
from scipy import stats

from .features import TARGET


def metrics(actual: pd.Series, pred: pd.Series) -> dict[str, float]:
    ok = actual.notna() & pred.notna()
    a, p = actual[ok], pred[ok]
    err = p - a
    return {
        "MAPE_%": float(np.mean(np.abs(err) / a) * 100),
        "MAE_MW": float(np.mean(np.abs(err))),
        "RMSE_MW": float(np.sqrt(np.mean(err**2))),
        "bias_MW": float(np.mean(err)),
        "hours": int(ok.sum()),
    }


def segments(df: pd.DataFrame) -> dict[str, pd.Series]:
    """Boolean masks for the situations that matter in load forecasting."""
    midday = df["hour"].between(10, 16)
    return {
        "all hours": pd.Series(True, index=df.index),
        "working days": (df["is_offday"] == 0) & (df["bridge"] == 0),
        "weekends": df["dow"] >= 5,
        "public holidays": df["holiday_share"] >= 0.5,
        "bridge days": df["bridge"] == 1,
        "Christmas period": df["xmas"] == 1,
        "sunny off-day middays": (df["is_offday"] == 1) & midday & (df["rad"] >= 500),
    }


def segment_table(df: pd.DataFrame, preds: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for name, mask in segments(df).items():
        row = {"segment": name, "hours": int(mask.sum())}
        for model in preds.columns:
            row[model] = metrics(df.loc[mask, TARGET], preds.loc[mask, model])["MAPE_%"]
        rows.append(row)
    return pd.DataFrame(rows).set_index("segment")


def dm_on_losses(loss_a: pd.Series, loss_b: pd.Series, date: pd.Series, lags: int = 7) -> dict:
    """Diebold-Mariano test on any per-hour losses (absolute error, pinball loss, ...).

    Hourly losses are strongly autocorrelated, so the test is run on daily
    mean losses with a Newey-West variance (HAC, `lags` days).
    A negative statistic means A has the lower loss.
    """
    d = (loss_a.groupby(date).mean() - loss_b.groupby(date).mean()).dropna()
    n = len(d)
    dc = d - d.mean()
    var = np.sum(dc**2) / n
    for k in range(1, lags + 1):
        var += 2 * (1 - k / (lags + 1)) * np.sum(dc.iloc[k:].to_numpy() * dc.iloc[:-k].to_numpy()) / n
    stat = d.mean() / np.sqrt(var / n)
    p = 2 * (1 - stats.norm.cdf(abs(stat)))
    return {"days": n, "mean_daily_loss_diff": float(d.mean()), "DM_stat": float(stat), "p_value": float(p)}


def diebold_mariano(df: pd.DataFrame, pred_a: pd.Series, pred_b: pd.Series, lags: int = 7) -> dict:
    """Is model A's absolute error significantly different from model B's?

    A negative statistic means A is more accurate than B.
    """
    r = dm_on_losses((pred_a - df[TARGET]).abs(), (pred_b - df[TARGET]).abs(), df["date"], lags)
    r["mean_daily_MAE_diff_MW"] = r.pop("mean_daily_loss_diff")
    return r
