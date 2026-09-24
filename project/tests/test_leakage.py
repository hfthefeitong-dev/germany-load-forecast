"""The fairness rule, checked automatically.

Idea: if the features for day D were built only from information available
at the start of day D-1, then changing the load on day D-1 or day D must not
change them. We scramble exactly that data and compare.
"""

import numpy as np
import pandas as pd

from loadfc import config, features


def _toy(days: int = 40) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(0)
    idx = pd.date_range("2026-03-01", periods=days * 24, freq="h", tz="UTC")
    series = pd.DataFrame(
        {
            "load_actual": 50_000 + rng.normal(0, 5_000, len(idx)),
            "load_official": 50_000 + rng.normal(0, 5_000, len(idx)),
            "price_da": rng.normal(90, 30, len(idx)),
        },
        index=idx,
    )
    weather = pd.DataFrame(
        {c: rng.normal(size=len(idx)) for c in ["temp", "cloud", "rad", "rad_south"]},
        index=idx,
    )
    return series, weather


def test_features_do_not_see_day_before_or_same_day():
    series, weather = _toy()
    base = features.build(series, weather)

    # Pick a day in the middle, then scramble the load of D-1 and D.
    D = pd.Timestamp("2026-03-25")
    local_date = series.index.tz_convert(config.TZ).normalize().tz_localize(None)
    forbidden = (local_date == D) | (local_date == D - pd.Timedelta(days=1))
    tampered = series.copy()
    tampered.loc[forbidden, "load_actual"] *= 3

    after = features.build(tampered, weather)
    rows = base["date"] == D
    pd.testing.assert_frame_equal(base.loc[rows, features.FEATURES], after.loc[rows, features.FEATURES])


def test_tampering_day_minus_two_does_change_features():
    """Sanity check of the test itself: D-2 *is* allowed, so it must matter."""
    series, weather = _toy()
    base = features.build(series, weather)

    D = pd.Timestamp("2026-03-25")
    local_date = series.index.tz_convert(config.TZ).normalize().tz_localize(None)
    tampered = series.copy()
    tampered.loc[local_date == D - pd.Timedelta(days=2), "load_actual"] *= 3

    after = features.build(tampered, weather)
    rows = base["date"] == D
    assert not base.loc[rows, "load_lag48"].equals(after.loc[rows, "load_lag48"])
