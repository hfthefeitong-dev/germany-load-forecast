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
"""

import pandas as pd

from . import config
from .features import TARGET

COVARIATES = ["temp", "cloud", "rad", "rad_south", "holiday_share", "is_offday", "bridge", "xmas", "hour", "dow"]
CONTEXT_HOURS = 2048   # about 12 weeks of history per forecast
HORIZON = 50           # from D-1 00:00 to the end of D, with slack for DST days


def _frames(df: pd.DataFrame, day: pd.Timestamp, covariates: list[str]):
    """Context and future tables for one forecast day `day` (local midnight)."""
    cut = (day - pd.Timedelta(days=1)).tz_convert("UTC")
    ctx = df[(df.index < cut) & (df.index >= cut - pd.Timedelta(hours=CONTEXT_HOURS))]
    fut = df[(df.index >= cut) & (df.index < cut + pd.Timedelta(hours=HORIZON))]

    key = day.strftime("%Y-%m-%d")
    c = ctx[[TARGET, *covariates]].copy()
    c["id"], c["timestamp"] = key, c.index.tz_localize(None)
    f = fut[covariates].copy()
    f["id"], f["timestamp"] = key, f.index.tz_localize(None)
    return c.reset_index(drop=True), f.reset_index(drop=True)


def forecast(df: pd.DataFrame, days: list[pd.Timestamp], covariates: list[str], batch: int = 32) -> pd.Series:
    from chronos import Chronos2Pipeline  # imported here: heavy, GPU-only dependency

    pipe = Chronos2Pipeline.from_pretrained("amazon/chronos-2", device_map="cuda")
    out = []
    for i in range(0, len(days), batch):
        chunk = days[i : i + batch]
        pairs = [_frames(df, d, covariates) for d in chunk]
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
        print(f"chronos: {min(i + batch, len(days))}/{len(days)} days")
    return pd.concat(out).astype("float64")


def test_days(df: pd.DataFrame) -> list[pd.Timestamp]:
    """Forecast days in the test period where all covariates are available."""
    local = df.index.tz_convert(config.TZ)
    last_weather = local[df["temp"].notna()].max().normalize()
    last_actual = local[df[TARGET].notna()].max().normalize()
    end = min(last_weather, last_actual)
    return list(pd.date_range(config.TEST_START, end, freq="D"))
