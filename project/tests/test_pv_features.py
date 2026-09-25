"""PV capacity features: correct lag, and no information from day D-1 or later."""

import numpy as np
import pandas as pd

from loadfc import config, features


def _toy():
    rng = np.random.default_rng(2)
    idx = pd.date_range("2026-03-01", periods=60 * 24, freq="h", tz="UTC")
    series = pd.DataFrame({"load_actual": 50_000 + rng.normal(0, 5_000, len(idx)),
                           "load_official": 50_000.0, "price_da": 90.0}, index=idx)
    weather = pd.DataFrame({c: rng.uniform(0, 800, len(idx)) for c in ["temp", "cloud", "rad", "rad_south"]}, index=idx)
    months = pd.date_range("2025-10-01", "2026-06-01", freq="MS")
    cap = pd.DataFrame({"pv_gw": np.arange(len(months)) + 100.0,
                        "battery_gw": 10.0, "battery_gwh": np.arange(len(months)) + 20.0}, index=months)
    return series, weather, cap


def test_capacity_is_lagged_two_months():
    series, weather, cap = _toy()
    f = features.add_pv_features(features.build(series, weather), cap)
    april = f[f["date"] == pd.Timestamp("2026-04-15")]
    assert (april["pv_gw"] == cap.loc["2026-02-01", "pv_gw"]).all()


def test_pv_features_ignore_load_of_d1_and_d():
    series, weather, cap = _toy()
    base = features.add_pv_features(features.build(series, weather), cap)
    D = pd.Timestamp("2026-04-10")
    date = series.index.tz_convert(config.TZ).normalize().tz_localize(None)
    tampered = series.copy()
    tampered.loc[(date == D) | (date == D - pd.Timedelta(days=1)), "load_actual"] *= 3
    after = features.add_pv_features(features.build(tampered, weather), cap)
    rows = base["date"] == D
    cols = features.FEATURES + features.PV_FEATURES
    pd.testing.assert_frame_equal(base.loc[rows, cols], after.loc[rows, cols])
