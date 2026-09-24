import pandas as pd
import pytest

from loadfc import calendar_de, config

CAL = calendar_de.daily_calendar(pd.Timestamp("2026-01-01"), pd.Timestamp("2026-12-31"))


def test_national_holiday_is_everyone():
    assert CAL.loc["2026-05-01", "holiday_share"] == pytest.approx(1.0, abs=1e-3)


def test_epiphany_only_three_states():
    expected = sum(config.POP_WEIGHTS[s] for s in ("BW", "BY", "ST"))
    assert CAL.loc["2026-01-06", "holiday_share"] == pytest.approx(expected, abs=1e-3)


def test_friday_after_ascension_is_bridge_day():
    # Easter 2026 is 5 April, so Ascension is Thursday 14 May.
    assert CAL.loc["2026-05-14", "holiday_share"] == pytest.approx(1.0, abs=1e-3)
    assert CAL.loc["2026-05-15", "bridge"] == 1


def test_christmas_flag():
    assert CAL.loc["2026-12-28", "xmas"] == 1
    assert CAL.loc["2026-12-10", "xmas"] == 0
