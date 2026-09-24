"""The fairness rule, checked automatically.

Idea: if the features for day D were built only from information available
at the start of day D-1, then changing the load on day D-1 or day D must not
change them. We scramble exactly that data and compare.
"""

import numpy as np
import pytest
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


def test_morning_features_only_see_d1_before_cutoff():
    """Morning features may use D-1 before 08:00, nothing later."""
    series, weather = _toy()
    base = features.add_morning_load(features.build(series, weather))
    cols = features.FEATURES + features.MORNING_FEATURES

    D = pd.Timestamp("2026-03-25")
    local = series.index.tz_convert(config.TZ)
    date = local.normalize().tz_localize(None)
    forbidden = (date == D) | ((date == D - pd.Timedelta(days=1)) & (local.hour >= features.MORNING_UNTIL))
    tampered = series.copy()
    tampered.loc[forbidden, "load_actual"] *= 3
    after = features.add_morning_load(features.build(tampered, weather))
    rows = base["date"] == D
    pd.testing.assert_frame_equal(base.loc[rows, cols], after.loc[rows, cols])

    # ...while the allowed morning hours of D-1 do change them.
    allowed = (date == D - pd.Timedelta(days=1)) & (local.hour < features.MORNING_UNTIL)
    tampered = series.copy()
    tampered.loc[allowed, "load_actual"] *= 3
    after = features.add_morning_load(features.build(tampered, weather))
    assert not base.loc[rows, "load_d1_morning_mean"].equals(after.loc[rows, "load_d1_morning_mean"])


@pytest.mark.parametrize("start, D", [
    ("2026-10-01", "2026-10-26"),  # the day after clocks go back (D-1 has 25 hours)
    ("2026-03-05", "2026-03-30"),  # the day after clocks go forward (D-1 has 23 hours)
])
def test_no_leak_around_daylight_saving_changes(start, D):
    """A fixed 48 h shift is not "two days earlier" when D-1 has 23 or 25 hours."""
    rng = np.random.default_rng(0)
    idx = pd.date_range(start, periods=40 * 24, freq="h", tz="UTC")
    series = pd.DataFrame({"load_actual": 50_000 + rng.normal(0, 5_000, len(idx)),
                           "load_official": 50_000.0, "price_da": 90.0}, index=idx)
    weather = pd.DataFrame({c: rng.normal(size=len(idx)) for c in ["temp", "cloud", "rad", "rad_south"]}, index=idx)
    base = features.build(series, weather)

    D = pd.Timestamp(D)
    date = series.index.tz_convert(config.TZ).normalize().tz_localize(None)
    tampered = series.copy()
    tampered.loc[(date == D) | (date == D - pd.Timedelta(days=1)), "load_actual"] *= 3
    after = features.build(tampered, weather)
    rows = base["date"] == D
    pd.testing.assert_frame_equal(base.loc[rows, features.FEATURES], after.loc[rows, features.FEATURES])
