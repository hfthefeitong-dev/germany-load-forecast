"""Download reBAP, the German imbalance price, from netztransparenz.de.

reBAP ("regelzonenuebergreifender einheitlicher Bilanzausgleichsenergiepreis")
is the price at which every balance responsible party settles the gap
between what it scheduled and what actually happened. It is published per
15 minutes and is symmetric: the same price applies to being short or long.

netztransparenz.de offers a CSV download button on its public reBAP page.
The button issues a GET request with a base64-encoded JSON description of
the query; this module sends exactly the same request.
"""

import base64
import io
import json
import time

import pandas as pd
import requests

URL = "https://www.netztransparenz.de/DesktopModules/LotesCharts/CsvDownloadHandler.ashx"

# Copied from the page configuration of the chart "reBAP unterdeckt"
# (quality-assured values).
SETTINGS = {
    "DataType": 20,
    "ProduktId": 10,
    "CultureName": "de-DE",
    "Title": "reBAP unterdeckt",
    "DiagramType": "line",
    "TimeInterval": 15,
    "DataUnit": "EUR/MWh",
    "CsvColumns": ["50Hertz", "Amprion", "TenneT TSO", "TransnetBW"],
    "TsoIds": [0],
    "NrvDirection": 0,
    "WebApiRoute": "NrvSaldo/rebap/qualitaetsgesichert",
    # Required: without it the server answers with an "internal error" text.
    "WebApiBaseUri": "https://lotes-UNB-svc-netzt.corp.transmission-it.de/StatistikApi/",
}


def _fetch_month(first: pd.Timestamp) -> pd.DataFrame:
    last = first + pd.offsets.MonthBegin(1)
    request = {
        "LocalFrom": first.strftime("%Y-%m-%d"),
        "LocalTo": last.strftime("%Y-%m-%d"),
        "ResultTimeZone": "utc",
        "Settings": SETTINGS,
    }
    encoded = base64.b64encode(json.dumps(request).encode()).decode()
    r = requests.get(
        URL, params={"request": encoded}, headers={"User-Agent": "Mozilla/5.0"}, timeout=120
    )
    r.raise_for_status()
    text = r.content.decode("utf-8-sig")
    if not text.strip() or ";" not in text.splitlines()[0]:
        # The server returns HTTP 200 with a plain-text message on failure,
        # so a silent empty result would hide errors. Fail loudly instead.
        raise RuntimeError(f"reBAP download failed for {first:%Y-%m}: {text[:120]!r}")

    df = pd.read_csv(io.StringIO(text), sep=";", decimal=",")
    stamp = pd.to_datetime(df["Datum"] + " " + df["von"], format="%d.%m.%Y %H:%M", utc=True)
    # .to_numpy() matters: passing a Series together with a new index makes
    # pandas *align* on index labels (0, 1, 2, ... vs timestamps), which
    # silently yields all-NaN. A plain array is placed row by row instead.
    values = pd.to_numeric(df["reBAP unterdeckt"], errors="coerce").to_numpy()
    return pd.DataFrame({"rebap": values}, index=pd.DatetimeIndex(stamp))


def download(start: pd.Timestamp, end: pd.Timestamp) -> pd.Series:
    """Quarter-hourly reBAP between `start` and `end`, aggregated to hourly means."""
    months = pd.date_range(start.tz_localize(None).normalize().replace(day=1), end.tz_localize(None), freq="MS")
    frames = []
    for m in months:
        frames.append(_fetch_month(m))
        time.sleep(0.3)
    q = pd.concat(frames).sort_index()
    q = q[~q.index.duplicated(keep="last")]["rebap"]
    hourly = q.resample("1h").mean()
    hourly.index.name = "time_utc"
    return hourly
