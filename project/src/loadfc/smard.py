"""Download hourly series from SMARD, the data platform of the Bundesnetzagentur.

SMARD serves each series as weekly JSON chunks:
    index_hour.json            -> list of chunk start timestamps (ms, UTC)
    {id}_{region}_hour_{t}.json -> [[timestamp_ms, value], ...]

Series used here
    410   actual grid load, Germany                        (MWh per hour)
    411   official day-ahead load forecast, Germany        (MWh per hour)
    4169  day-ahead wholesale price, bidding zone DE-LU    (EUR/MWh)

The official forecast is produced by the four transmission system
operators and published on SMARD by 18:00 on the day before delivery.
"""

import time

import pandas as pd

from . import config, net

BASE = "https://www.smard.de/app/chart_data"

SERIES = {
    "load_actual": (410, "DE"),
    "load_official": (411, "DE"),
    "price_da": (4169, "DE-LU"),
}


def _get(url: str) -> dict:
    return net.get_json(url, timeout=60)


def fetch(name: str, start: pd.Timestamp) -> pd.Series:
    """Download one series from `start` until the latest available hour."""
    fid, region = SERIES[name]
    chunks = _get(f"{BASE}/{fid}/{region}/index_hour.json")["timestamps"]

    # A chunk covers one week, so start one chunk early to be safe.
    start_ms = start.tz_convert("UTC").value // 10**6 - 7 * 24 * 3600 * 1000
    chunks = [t for t in chunks if t >= start_ms]

    rows: list[tuple[int, float]] = []
    for t in chunks:
        payload = _get(f"{BASE}/{fid}/{region}/{fid}_{region}_hour_{t}.json")
        rows += [(ts, v) for ts, v in payload["series"] if v is not None]
        time.sleep(0.1)  # be polite to a public service

    s = pd.Series(
        [v for _, v in rows],
        index=pd.to_datetime([ts for ts, _ in rows], unit="ms", utc=True),
        name=name,
        dtype="float64",
    )
    s = s[~s.index.duplicated(keep="last")].sort_index()
    return s[s.index >= start.tz_convert("UTC")]


def download_all(start: pd.Timestamp) -> pd.DataFrame:
    frames = [fetch(name, start) for name in SERIES]
    df = pd.concat(frames, axis=1)
    df.index.name = "time_utc"
    return df
