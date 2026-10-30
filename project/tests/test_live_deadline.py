"""The 12:00 deadline and the day before follow the calendar, also on DST days."""

import pandas as pd
import pytest

from loadfc import config, live


@pytest.mark.parametrize("day", ["2026-10-25", "2026-03-29", "2026-06-15"])
def test_deadline_is_wall_clock_noon(day):
    deadline = live._deadline(pd.Timestamp(day, tz=config.TZ), 12)
    assert deadline.tz_localize(None) == pd.Timestamp(day) + pd.Timedelta(hours=12)


def test_forecast_for_2026_10_26_was_on_time():
    # Issued at 11:17 on the 25-hour day; the old code put the deadline at 11:00.
    issued = pd.Timestamp("2026-10-25T11:17:26+01:00")
    assert issued < live._deadline(pd.Timestamp("2026-10-25", tz=config.TZ), 12)


@pytest.mark.parametrize("day,before", [("2026-10-26", "2026-10-25"),
                                        ("2026-03-30", "2026-03-29"),
                                        ("2026-06-15", "2026-06-14")])
def test_previous_day(day, before):
    assert live._previous_day(pd.Timestamp(day, tz=config.TZ)) == pd.Timestamp(before, tz=config.TZ)
