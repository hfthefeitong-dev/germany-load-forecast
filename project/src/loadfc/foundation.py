"""Zero-shot forecasts with Chronos-2, a pretrained time series foundation model.

Chronos-2 (Amazon, 2025, Apache-2.0) is a 120M-parameter transformer
pretrained on a large collection of time series. "Zero-shot" means it is
used as-is: it has never been trained on German load data. It reads the
recent history (the context) and predicts what comes next.

Same fairness rule as for LightGBM:
  * context ends at the start of day D-1, so the newest load value is from D-2
  * future covariates for D-1 and D are only calendar data and the 48 h-ahead
    weather forecast, which are known at that time

Two variants are compared:
  chronos_uni   load history only
  chronos_cov   load history plus known-future covariates

Context length is a hyperparameter. It is chosen on each window's
validation period, never on the test period. Longer context lets the model
see earlier holidays, but 8192 hours (the model's maximum) is 341 days, so
last year's Christmas is still out of reach.
"""

import pandas as pd

from . import config
from .features import TARGET

COVARIATES = ["temp", "cloud", "rad", "rad_south", "holiday_share", "is_offday", "bridge", "xmas", "hour", "dow"]
CONTEXT_OPTIONS = (2048, 8192)  # about 12 weeks, or the model maximum of about 11 months
HORIZON = 50                    # from D-1 00:00 to the end of D, with slack for DST days


def _frames(df: pd.DataFrame, day: pd.Timestamp, covariates: list[str], context_hours: int):
    """Context and future tables for one forecast day `day` (local midnight)."""
    cut = (day - pd.Timedelta(days=1)).tz_convert("UTC")
    # Never reach back before the weather archive starts: covariates would be missing.
    first = max(cut - pd.Timedelta(hours=context_hours), config.HISTORY_START.tz_convert("UTC"))
    ctx = df[(df.index < cut) & (df.index >= first)]
    fut = df[(df.index >= cut) & (df.index < cut + pd.Timedelta(hours=HORIZON))]

    key = day.strftime("%Y-%m-%d")
    c = ctx[[TARGET, *covariates]].copy()
    c["id"], c["timestamp"] = key, c.index.tz_localize(None)
    f = fut[covariates].copy()
    f["id"], f["timestamp"] = key, f.index.tz_localize(None)
    return c.reset_index(drop=True), f.reset_index(drop=True)


_PIPE = None


def _pipeline():
    """Load the model once per process."""
    global _PIPE
    if _PIPE is None:
        from chronos import Chronos2Pipeline  # heavy, GPU-only dependency

        _PIPE = Chronos2Pipeline.from_pretrained("amazon/chronos-2", device_map="cuda")
    return _PIPE


def forecast(
    df: pd.DataFrame, days: list[pd.Timestamp], covariates: list[str], context_hours: int, batch: int = 16
) -> pd.Series:
    pipe = _pipeline()
    out = []
    for i in range(0, len(days), batch):
        chunk = days[i : i + batch]
        pairs = [_frames(df, d, covariates, context_hours) for d in chunk]
        ctx = pd.concat([p[0] for p in pairs], ignore_index=True)
        fut = pd.concat([p[1] for p in pairs], ignore_index=True)
        kwargs = {"future_df": fut} if covariates else {}
        pred = pipe.predict_df(
            ctx, prediction_length=HORIZON, quantile_levels=[0.5],
            id_column="id", timestamp_column="timestamp", target=TARGET, **kwargs,
        )
        pred.index = pd.to_datetime(pred["timestamp"]).dt.tz_localize("UTC").dt.as_unit("ns")
        # Keep only the hours that belong to the forecast day itself.
        for d in chunk:
            p = pred[pred["id"] == d.strftime("%Y-%m-%d")]
            p = p[p.index.tz_convert(config.TZ).normalize() == d]
            out.append(p["predictions"])
    return pd.concat(out).astype("float64")


def days_between(df: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp | None) -> list[pd.Timestamp]:
    """Forecast days in [start, end) where covariates and actuals are available."""
    local = df.index.tz_convert(config.TZ)
    last = min(local[df["temp"].notna()].max(), local[df[TARGET].notna()].max()).normalize()
    if end is not None:
        last = min(last, end - pd.Timedelta(days=1))
    return list(pd.date_range(start, last, freq="D"))


def choose_context(df: pd.DataFrame, w: config.Window) -> tuple[int, dict[int, float]]:
    """Pick the context length with the lowest validation MAPE (with covariates)."""
    days = days_between(df, w.valid_start, w.test_start)
    scores = {}
    for hours in CONTEXT_OPTIONS:
        pred = forecast(df, days, COVARIATES, hours)
        y = df.loc[pred.index, TARGET]
        ok = y.notna()
        scores[hours] = float(((pred[ok] - y[ok]).abs() / y[ok]).mean() * 100)
        print(f"  {w.name} validation, context {hours} h: MAPE {scores[hours]:.2f}%")
    return min(scores, key=scores.get), scores
