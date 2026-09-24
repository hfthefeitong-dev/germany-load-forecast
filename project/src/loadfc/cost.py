"""Translate forecast errors into money.

Setting: a balance responsible party (Bilanzkreisverantwortlicher) buys its
forecast quantity F on the day-ahead market at price P_da. Reality turns out
to be A. The gap (A - F) is settled at the imbalance price reBAP.

    total cost        = F * P_da + (A - F) * reBAP
    cost if perfect   = A * P_da
    extra cost        = (A - F) * (reBAP - P_da)

So a forecast error is expensive exactly when the imbalance price moves
away from the day-ahead price in the wrong direction. Being short (A > F)
hurts when reBAP > P_da; being long hurts when reBAP < P_da.

Caveat: applying this to the whole of Germany treats the country as one
balancing group. That is a thought experiment. In reality reBAP itself
depends on the total imbalance, so it would change if everyone forecast
better. The numbers compare forecasts; they are not a market simulation.
"""

import pandas as pd

from .features import TARGET


def extra_cost(df: pd.DataFrame, pred: pd.Series) -> pd.Series:
    """Hourly extra cost in EUR (MW over one hour = MWh)."""
    return (df[TARGET] - pred) * (df["rebap"] - df["price_da"])


def cost_table(df: pd.DataFrame, preds: pd.DataFrame) -> pd.DataFrame:
    ok = df[[TARGET, "rebap", "price_da"]].notna().all(axis=1) & preds.notna().all(axis=1)
    energy = df.loc[ok, TARGET].sum()
    rows = []
    for model in preds.columns:
        c = extra_cost(df[ok], preds.loc[ok, model])
        rows.append({
            "model": model,
            "extra_cost_mEUR": c.sum() / 1e6,
            "EUR_per_MWh": c.sum() / energy,
            "hours": int(ok.sum()),
        })
    return pd.DataFrame(rows).set_index("model")
