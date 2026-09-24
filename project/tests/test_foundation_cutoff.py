"""Chronos-2's context must end exactly at the cutoff, also on DST days."""

import numpy as np
import pandas as pd
import pytest

from loadfc import config, foundation


@pytest.mark.parametrize("day", ["2026-10-26", "2026-03-30", "2026-06-15"])
@pytest.mark.parametrize("cut_hour", [0, 8])
def test_context_ends_at_cutoff(day, cut_hour):
    idx = pd.date_range("2026-01-01", "2026-12-31", freq="h", tz="UTC")
    df = pd.DataFrame({"load_actual": np.arange(len(idx), dtype=float), "temp": 1.0}, index=idx)
    D = pd.Timestamp(day, tz=config.TZ)
    ctx, fut = foundation._frames(df, D, ["temp"], context_hours=500, cut_hour=cut_hour)

    cutoff = pd.Timestamp(day) - pd.Timedelta(days=1) + pd.Timedelta(hours=cut_hour)  # local wall time
    last_ctx = pd.Timestamp(ctx["timestamp"].max(), tz="UTC").tz_convert(config.TZ).tz_localize(None)
    first_fut = pd.Timestamp(fut["timestamp"].min(), tz="UTC").tz_convert(config.TZ).tz_localize(None)
    assert last_ctx < cutoff <= first_fut
    assert last_ctx == cutoff - pd.Timedelta(hours=1)
