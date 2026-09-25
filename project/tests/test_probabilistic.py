"""Pinball loss and the rolling conformal intervals."""

import numpy as np
import pandas as pd
import pytest

from loadfc.experiments import QUANTILES, conformal, pinball


def test_pinball_known_values():
    y = pd.Series([100.0])
    q = pd.DataFrame({0.1: [90.0], 0.9: [120.0]})
    # tau 0.1: y above q by 10 -> 0.1 * 10 = 1;  tau 0.9: y below q by 20 -> 0.1 * 20 = 2
    assert pinball(y, q).iloc[0] == pytest.approx(1.5)


def _toy(days=80):
    rng = np.random.default_rng(3)
    idx = pd.date_range("2026-03-01", periods=days * 24, freq="h", tz="UTC")
    local = idx.tz_convert("Europe/Berlin")
    date = pd.Series(local.normalize().tz_localize(None), index=idx)
    hour = pd.Series(local.hour, index=idx)
    actual = pd.Series(50_000 + rng.normal(0, 3_000, len(idx)), index=idx)
    point = actual + rng.normal(0, 1_000, len(idx))
    return point, actual, date, hour


def test_conformal_ignores_day_before_and_same_day():
    point, actual, date, hour = _toy()
    D = pd.Timestamp("2026-05-01")
    base = conformal(point, actual, date, hour, window_days=28)
    tampered = actual.copy()
    tampered[(date == D) | (date == D - pd.Timedelta(days=1))] *= 3
    after = conformal(point, tampered, date, hour, window_days=28)
    rows = date == D
    pd.testing.assert_frame_equal(base[rows], after[rows])


def test_conformal_intervals_are_ordered_and_roughly_calibrated():
    point, actual, date, hour = _toy()
    q = conformal(point, actual, date, hour, window_days=28).dropna()
    assert (q.diff(axis=1).iloc[:, 1:] >= 0).all().all()
    y = actual.loc[q.index]
    coverage = ((y >= q[0.1]) & (y <= q[0.9])).mean()
    assert 0.7 < coverage < 0.9
