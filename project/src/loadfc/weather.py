"""Weather *forecasts* as they were known two days before delivery.

Why forecasts and not observations: the official load forecast for day D is
made on day D-1. A model that uses the weather actually observed on day D
would be looking into the future, and any comparison would be unfair.

Source: Open-Meteo Previous Runs API. A variable with the suffix
`_previous_day2` returns, for each hour T, the value that the weather model
predicted 48 hours before T. For every hour of day D this forecast was
issued on day D-2, i.e. before the official forecast is published.

Note: Open-Meteo's *Historical Forecast* API is a different product. It
stitches together the first hours of each model run, so its lead time is
only a few hours and it would leak information. It is not used here.
"""

import pandas as pd
import requests

from . import config

URL = "https://previous-runs-api.open-meteo.com/v1/forecast"
VARIABLES = ("temperature_2m", "shortwave_radiation", "cloud_cover")
LEAD = "previous_day2"


def _fetch_block(start: str, end: str, url: str = URL, suffix: str = f"_{LEAD}") -> pd.DataFrame:
    params = {
        "latitude": ",".join(str(s.lat) for s in config.STATES),
        "longitude": ",".join(str(s.lon) for s in config.STATES),
        "start_date": start,
        "end_date": end,
        "hourly": ",".join(f"{v}{suffix}" for v in VARIABLES),
        "timezone": "UTC",
    }
    r = requests.get(url, params=params, timeout=180)
    r.raise_for_status()
    payload = r.json()

    frames = []
    for state, loc in zip(config.STATES, payload):
        h = loc["hourly"]
        idx = pd.to_datetime(h["time"], utc=True)
        cols = {f"{v}__{state.code}": h[f"{v}{suffix}"] for v in VARIABLES}
        frames.append(pd.DataFrame(cols, index=idx, dtype="float64"))
    return pd.concat(frames, axis=1)


def download(start: pd.Timestamp, end: pd.Timestamp, url: str = URL, suffix: str = f"_{LEAD}") -> pd.DataFrame:
    """Per-state hourly forecasts, one request per calendar year."""
    blocks = []
    for year in range(start.year, end.year + 1):
        a = max(start, pd.Timestamp(f"{year}-01-01", tz=start.tz))
        b = min(end, pd.Timestamp(f"{year}-12-31", tz=start.tz))
        blocks.append(_fetch_block(a.strftime("%Y-%m-%d"), b.strftime("%Y-%m-%d"), url, suffix))
    df = pd.concat(blocks).sort_index()
    df = df[~df.index.duplicated(keep="last")]
    df.index.name = "time_utc"
    return df


# Observed weather (ERA5 reanalysis). ONLY for the upper-bound experiment in
# experiments.py: it measures how much accuracy is lost because weather
# forecasts are imperfect. Using it in a real forecast would be cheating.
ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"


def download_observed(start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    return download(start, end, url=ARCHIVE_URL, suffix="")


def aggregate(per_state: pd.DataFrame) -> pd.DataFrame:
    """Collapse 16 states into a few national features.

    Weighted means ignore missing states and re-normalise the weights, so a
    single missing city does not turn the national value into NaN.
    """

    def weighted(var: str, codes: list[str], weights: dict[str, float]) -> pd.Series:
        cols = [f"{var}__{c}" for c in codes]
        w = pd.Series({f"{var}__{c}": weights[c] for c in codes})
        values = per_state[cols]
        mask = values.notna()
        num = (values.fillna(0) * w).sum(axis=1)
        den = (mask * w).sum(axis=1)
        return (num / den).where(den > 0)

    codes = [s.code for s in config.STATES]
    equal = {c: 1.0 for c in codes}
    out = pd.DataFrame(index=per_state.index)
    out["temp"] = weighted("temperature_2m", codes, config.POP_WEIGHTS)
    out["cloud"] = weighted("cloud_cover", codes, config.POP_WEIGHTS)
    out["rad"] = weighted("shortwave_radiation", codes, config.POP_WEIGHTS)
    out["rad_south"] = weighted("shortwave_radiation", list(config.SOUTH), equal)
    return out
