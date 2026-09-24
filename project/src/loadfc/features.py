"""Build the feature table.

THE FAIRNESS RULE
-----------------
The official forecast for day D is published on day D-1. Our forecast for
day D may therefore only use information available at the start of D-1:

  * load: only values from day D-2 or earlier    -> lags of at least 48 h
  * weather: only forecasts issued >= 48 h ahead -> `_previous_day2`
  * calendar: known years in advance             -> always allowed

This is stricter than what the official forecaster can use, so any win is
not the result of seeing more information. `tests/test_leakage.py` checks
the rule automatically.
"""

import numpy as np
import pandas as pd

from . import calendar_de, config

TARGET = "load_actual"

FEATURES = [
    # calendar
    "hour", "dow", "doy_sin", "doy_cos",
    "holiday_share", "is_offday", "bridge", "xmas",
    "holiday_share_lag2", "holiday_share_lag7",
    # load history (>= 48 h old)
    "load_lag48", "load_lag168", "load_lag336",
    "load_daymean_lag2", "load_daymean_lag7",
    # weather forecast issued 48 h ahead
    "temp", "cloud", "rad", "rad_south",
    "temp_daymean", "rad_daymean",
]


def to_ns(df: pd.DataFrame) -> pd.DataFrame:
    """Unify timestamp resolution.

    Parquet files come back with ms or us resolution depending on the
    source. Joining indexes of different resolutions degrades them to a
    plain object Index in pandas 3, so everything is converted to ns.
    """
    df = df.copy()
    df.index = pd.DatetimeIndex(df.index).as_unit("ns")
    return df


def build(series: pd.DataFrame, weather: pd.DataFrame) -> pd.DataFrame:
    """Combine SMARD series and aggregated weather into one hourly table.

    Parameters
    ----------
    series  : hourly, UTC index; columns load_actual, load_official, price_da
    weather : hourly, UTC index; columns temp, cloud, rad, rad_south
    """
    series, weather = to_ns(series), to_ns(weather)

    # A gap-free hourly UTC index makes `shift(48)` mean "48 hours earlier".
    idx = pd.date_range(series.index.min(), series.index.max(), freq="h", tz="UTC").as_unit("ns")
    df = series.reindex(idx).join(weather.reindex(idx))
    df.index.name = "time_utc"

    local = df.index.tz_convert(config.TZ)
    df["date"] = local.normalize().tz_localize(None)  # local calendar day
    df["hour"] = local.hour
    doy = local.dayofyear.to_numpy()
    df["doy_sin"] = np.sin(2 * np.pi * doy / 365.25)
    df["doy_cos"] = np.cos(2 * np.pi * doy / 365.25)

    # ---- calendar, mapped from a daily table
    cal = calendar_de.daily_calendar(df["date"].min() - pd.Timedelta(days=14), df["date"].max())
    for col in ["holiday_share", "dow", "is_offday", "bridge", "xmas"]:
        df[col] = df["date"].map(cal[col])
    df["holiday_share_lag2"] = (df["date"] - pd.Timedelta(days=2)).map(cal["holiday_share"])
    df["holiday_share_lag7"] = (df["date"] - pd.Timedelta(days=7)).map(cal["holiday_share"])

    # ---- load history
    load = df[TARGET]
    df["load_lag48"] = load.shift(48)
    df["load_lag168"] = load.shift(168)
    df["load_lag336"] = load.shift(336)

    # Daily means are only used for days that are complete by the start of D-1.
    daily = load.groupby(df["date"]).mean()
    df["load_daymean_lag2"] = (df["date"] - pd.Timedelta(days=2)).map(daily)
    df["load_daymean_lag7"] = (df["date"] - pd.Timedelta(days=7)).map(daily)

    # ---- weather: daily summaries of the *forecast* for day D
    df["temp_daymean"] = df.groupby("date")["temp"].transform("mean")
    df["rad_daymean"] = df.groupby("date")["rad"].transform("mean")

    return df
