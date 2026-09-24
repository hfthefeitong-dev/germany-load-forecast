"""German calendar features on a daily grid.

Named calendar_de rather than calendar so it does not shadow the standard
library module `calendar`.

Public holidays differ by state (e.g. Epiphany only in BW, BY and ST), so a
yes/no flag is too coarse. `holiday_share` is the share of Germany's
population that has the day off, between 0 and 1.
"""

import holidays
import numpy as np
import pandas as pd

from . import config


def daily_calendar(first: pd.Timestamp, last: pd.Timestamp) -> pd.DataFrame:
    """One row per local calendar day, index = naive midnight timestamps."""
    days = pd.date_range(first, last, freq="D")
    years = list(range(days.min().year, days.max().year + 1))

    share = np.zeros(len(days))
    for s in config.STATES:
        cal = holidays.Germany(subdiv=s.code, years=years)
        share += np.array([d.date() in cal for d in days]) * config.POP_WEIGHTS[s.code]

    out = pd.DataFrame(index=days)
    out["holiday_share"] = share.round(4)
    out["dow"] = days.dayofweek  # Monday = 0

    # A day counts as "off" for most people if it is a weekend or a holiday
    # for the majority of the population.
    off = (out["dow"] >= 5) | (out["holiday_share"] >= 0.5)
    out["is_offday"] = off.astype(int)

    # Bridge day ("Brueckentag"): a working day squeezed between two off
    # days, e.g. the Friday after Ascension. Many people take it off.
    prev_off = off.shift(1, fill_value=False)
    next_off = off.shift(-1, fill_value=False)
    out["bridge"] = (~off & prev_off & next_off).astype(int)

    # Between Christmas Eve and New Year demand behaves like a long holiday.
    md = days.month * 100 + days.day
    out["xmas"] = ((md >= 1224) | (md <= 101)).astype(int)
    return out
