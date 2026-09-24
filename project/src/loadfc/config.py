"""Central configuration: paths, time ranges, and the 16 German states.

Everything that a reader might want to change lives here, so the other
modules contain logic only.
"""

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

# --------------------------------------------------------------------- paths
ROOT = Path(__file__).resolve().parents[2]  # .../project
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
REPORTS = ROOT / "reports"
FIGURES = REPORTS / "figures"

TZ = "Europe/Berlin"

# ---------------------------------------------------------------- time range
# The weather archive with genuine 48 h-ahead forecasts starts on 2024-01-20
# (Open-Meteo Previous Runs API), so that is where usable history begins.
HISTORY_START = pd.Timestamp("2024-01-21", tz=TZ)

# Everything from TEST_START onwards is out-of-sample. Hyperparameters are
# chosen on data *before* this date only.
TEST_START = pd.Timestamp("2025-10-01", tz=TZ)

# Validation window used once, before the test period, to pick the number
# of boosting rounds.
VALID_START = pd.Timestamp("2025-07-01", tz=TZ)


# -------------------------------------------------------------------- states
@dataclass(frozen=True)
class State:
    code: str        # ISO 3166-2 suffix, as used by the `holidays` package
    city: str        # representative city whose weather stands in for the state
    lat: float
    lon: float
    population: float  # millions, Destatis 2023 (rounded)


STATES: list[State] = [
    State("BW", "Stuttgart",   48.78,  9.18, 11.28),
    State("BY", "Munich",      48.14, 11.58, 13.37),
    State("BE", "Berlin",      52.52, 13.40,  3.76),
    State("BB", "Potsdam",     52.40, 13.07,  2.57),
    State("HB", "Bremen",      53.08,  8.80,  0.68),
    State("HH", "Hamburg",     53.55,  9.99,  1.89),
    State("HE", "Frankfurt",   50.11,  8.68,  6.39),
    State("MV", "Rostock",     54.09, 12.10,  1.63),
    State("NI", "Hanover",     52.37,  9.73,  8.14),
    State("NW", "Cologne",     50.94,  6.96, 18.14),
    State("RP", "Mainz",       50.00,  8.27,  4.16),
    State("SL", "Saarbruecken", 49.23, 7.00,  0.99),
    State("SN", "Dresden",     51.05, 13.74,  4.09),
    State("ST", "Magdeburg",   52.13, 11.63,  2.19),
    State("SH", "Kiel",        54.32, 10.13,  2.95),
    State("TH", "Erfurt",      50.98, 11.03,  2.13),
]

POP_WEIGHTS: dict[str, float] = {
    s.code: s.population / sum(x.population for x in STATES) for s in STATES
}

# Southern states host a large share of Germany's rooftop PV.
SOUTH = ("BW", "BY")


def ensure_dirs() -> None:
    for d in (DATA_RAW, DATA_PROCESSED, FIGURES):
        d.mkdir(parents=True, exist_ok=True)
