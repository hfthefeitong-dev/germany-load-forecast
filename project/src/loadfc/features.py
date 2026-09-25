"""Build the feature table.

THE FAIRNESS RULE
-----------------
The official forecast for day D is published on day D-1. Our forecast for
day D may therefore only use information available at the start of D-1:

  * load: only values from day D-2 or earlier    -> same hour 2, 7, 14 days back
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

    # ---- load history: the same local hour 2, 7 and 14 days earlier.
    # Looked up by (local date, local hour), not by shifting a fixed number of
    # hours: when day D-1 has 25 hours (clocks going back), "48 hours before"
    # the last hour of D is midnight of D-1, which is not yet known at
    # forecast time. The names keep the familiar lag in hours.
    load = df[TARGET]
    by_day_hour = load.groupby([df["date"], df["hour"]]).mean()
    for days, col in [(2, "load_lag48"), (7, "load_lag168"), (14, "load_lag336")]:
        key = pd.MultiIndex.from_arrays([df["date"] - pd.Timedelta(days=days), df["hour"]])
        df[col] = by_day_hour.reindex(key).to_numpy()

    # Daily means are only used for days that are complete by the start of D-1.
    daily = load.groupby(df["date"]).mean()
    df["load_daymean_lag2"] = (df["date"] - pd.Timedelta(days=2)).map(daily)
    df["load_daymean_lag7"] = (df["date"] - pd.Timedelta(days=7)).map(daily)

    # ---- weather: daily summaries of the *forecast* for day D
    df["temp_daymean"] = df.groupby("date")["temp"].transform("mean")
    df["rad_daymean"] = df.groupby("date")["rad"].transform("mean")

    return df


# ------------------------------------------------------ fresher load (experiment)
# Assumption: the forecast is issued on day D-1 at 10:00 local time, before the
# day-ahead gate closure (12:00) and before the official forecast (18:00).
# SMARD publishes actual load with about 1 h delay (measured 2026-09-24), so
# with a 2 h safety margin the load of D-1 from 00:00 to 07:59 is known.
MORNING_UNTIL = 8

MORNING_FEATURES = [
    "load_d1_morning_mean",   # mean load of D-1, 00:00-07:59
    "load_d8_morning_mean",   # same window one week earlier, for comparison
    "load_d1_morning_ratio",  # this week's level relative to last week's
    "load_d1_last",           # the newest published hour, D-1 07:00
    "load_d1_same_hour",      # same hour on D-1, only for hours before 08:00
]


def add_morning_load(df: pd.DataFrame, until: int = MORNING_UNTIL) -> pd.DataFrame:
    """Add load features from the published morning of day D-1.

    Lookups use (local date, local hour) rather than a fixed 24 h shift: on
    daylight-saving days a 24 h shift would land one hour later and could
    peek past the cutoff.
    """
    df = df.copy()
    load = df[TARGET]
    known = df["hour"] < until
    by_day_hour = load.groupby([df["date"], df["hour"]]).mean()
    morning = load.where(known).groupby(df["date"]).mean()

    d1 = df["date"] - pd.Timedelta(days=1)
    d8 = df["date"] - pd.Timedelta(days=8)
    df["load_d1_morning_mean"] = d1.map(morning)
    df["load_d8_morning_mean"] = d8.map(morning)
    df["load_d1_morning_ratio"] = df["load_d1_morning_mean"] / df["load_d8_morning_mean"]
    last = pd.MultiIndex.from_arrays([d1, pd.Series(until - 1, index=df.index)])
    df["load_d1_last"] = by_day_hour.reindex(last).to_numpy()
    same = pd.MultiIndex.from_arrays([d1, df["hour"]])
    df["load_d1_same_hour"] = by_day_hour.reindex(same).to_numpy()
    df.loc[~known, "load_d1_same_hour"] = float("nan")
    return df



# ------------------------------------------- PV and storage capacity (experiment)
# Monthly installed capacity from capacity.py, lagged by CAPACITY_LAG_MONTHS
# because the register is published with a delay.
CAPACITY_LAG_MONTHS = 2

PV_FEATURES = [
    "pv_gw",                 # installed PV, GWp
    "battery_gwh",           # installed battery storage, GWh
    "pv_potential",          # pv_gw x forecast radiation: PV output if all panels produced
    "pv_potential_south",    # same with radiation in the PV-heavy south
    "pv_potential_delta7",   # change against the same hour one week earlier
    "battery_evening",       # battery_gwh x daily mean radiation: how full batteries get
    "battery_evening_delta7",
]


def add_pv_features(df: pd.DataFrame, capacity: pd.DataFrame, lag_months: int = CAPACITY_LAG_MONTHS) -> pd.DataFrame:
    """Physics-motivated features for behind-the-meter PV and home batteries.

    Grid load drops when rooftop PV produces, roughly in proportion to
    installed capacity times irradiance. Capacity grows by about 1 % per
    month, so a model that only sees radiation cannot know that the same
    sunshine removes more load every year.

    The delta7 features compare with the same hour one week earlier. The
    model already sees last week's load (load_lag168), so the delta says how
    much more or less PV to expect than then. It also stays within the range
    seen in training, which matters because tree models do not extrapolate.
    """
    df = df.copy()
    month = df["date"].dt.to_period("M")
    cap = capacity.copy()
    cap.index = cap.index.to_period("M")
    source = month - lag_months
    for col in ["pv_gw", "battery_gwh"]:
        df[col] = source.map(cap[col]).astype("float64")

    df["pv_potential"] = df["pv_gw"] * df["rad"] / 1000        # GW-like index (1000 W/m2 = STC)
    df["pv_potential_south"] = df["pv_gw"] * df["rad_south"] / 1000
    df["battery_evening"] = df["battery_gwh"] * df["rad_daymean"] / 1000

    by_day_hour = df.groupby([df["date"], df["hour"]])[["pv_potential", "battery_evening"]].mean()
    key = pd.MultiIndex.from_arrays([df["date"] - pd.Timedelta(days=7), df["hour"]])
    week_ago = by_day_hour.reindex(key)
    df["pv_potential_delta7"] = df["pv_potential"].to_numpy() - week_ago["pv_potential"].to_numpy()
    df["battery_evening_delta7"] = df["battery_evening"].to_numpy() - week_ago["battery_evening"].to_numpy()
    return df
