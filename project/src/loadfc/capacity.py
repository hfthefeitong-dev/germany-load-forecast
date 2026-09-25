"""Installed PV and battery storage capacity in Germany, monthly.

Source: Energy-Charts by Fraunhofer ISE (https://energy-charts.info), which
compiles the Marktstammdatenregister of the Bundesnetzagentur. National
totals only: no split by federal state and no split into rooftop and
ground-mounted PV.

Caveat: the register receives late registrations, so older months are
revised upwards over time. This project uses today's vintage of the data,
not the one that was available at each forecast date. Capacity changes by
about 1 % per month, so the effect is small, and the two-month lag used in
features.py absorbs most of the publication delay.
"""

import pandas as pd
import requests

from . import config

URL = "https://api.energy-charts.info/installed_power"

COLUMNS = {
    "Solar DC": "pv_gw",                       # installed PV, GWp (DC side)
    "Battery storage (power)": "battery_gw",   # GW
    "Battery storage (capacity)": "battery_gwh",
}


def download() -> pd.DataFrame:
    r = requests.get(URL, params={"country": "de", "time_step": "monthly",
                                  "installation_decommission": "false"}, timeout=60)
    r.raise_for_status()
    d = r.json()
    months = pd.to_datetime(d["time"], format="%m.%Y")
    out = pd.DataFrame(index=months)
    for p in d["production_types"]:
        if p["name"] in COLUMNS:
            out[COLUMNS[p["name"]]] = pd.to_numeric(pd.Series(p["data"], index=months), errors="coerce")
    out.index.name = "month"
    return out


def load() -> pd.DataFrame:
    path = config.DATA_RAW / "installed_capacity.parquet"
    if not path.exists():
        config.ensure_dirs()
        download().to_parquet(path)
    return pd.read_parquet(path)
