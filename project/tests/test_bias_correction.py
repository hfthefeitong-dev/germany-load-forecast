"""The bias correction for day D may only use errors up to day D-2."""

import numpy as np
import pandas as pd
import pytest

from loadfc.experiments import correct


def _toy(days: int = 30):
    rng = np.random.default_rng(1)
    idx = pd.date_range("2026-03-01", periods=days * 24, freq="h", tz="UTC")
    local = idx.tz_convert("Europe/Berlin")
    date = pd.Series(local.normalize().tz_localize(None), index=idx)
    hour = pd.Series(local.hour, index=idx)
    actual = pd.Series(50_000 + rng.normal(0, 3_000, len(idx)), index=idx)
    pred = actual + 800 + rng.normal(0, 500, len(idx))  # biased forecast
    return pred, actual, date, hour


@pytest.mark.parametrize("by_hour", [False, True])
def test_correction_does_not_see_day_before_or_same_day(by_hour):
    pred, actual, date, hour = _toy()
    D = pd.Timestamp("2026-03-20")
    base = correct(pred, actual, date, hour, window_days=5, alpha=1.0, by_hour=by_hour)

    tampered = actual.copy()
    tampered[(date == D) | (date == D - pd.Timedelta(days=1))] *= 3
    after = correct(pred, tampered, date, hour, window_days=5, alpha=1.0, by_hour=by_hour)

    rows = date == D
    pd.testing.assert_series_equal(base[rows], after[rows])


def test_correction_removes_a_constant_bias():
    pred, actual, date, hour = _toy()
    fixed = correct(pred, actual, date, hour, window_days=7, alpha=1.0, by_hour=False)
    late = date >= pd.Timestamp("2026-03-10")
    assert abs((pred - actual)[late].mean()) > 700
    assert abs((fixed - actual)[late].mean()) < 150
