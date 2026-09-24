"""Forecasting models.

Two baselines and one machine-learning model:

  naive_weekly  load at the same hour one week earlier
  official      the TSOs' published day-ahead forecast (the benchmark to beat)
  lgbm          gradient-boosted trees on the features in features.py

The LightGBM model is evaluated like it would be used in practice: at the
start of every month it is retrained on all data known at that time, then
used to forecast the whole month. It never sees the month it predicts.
"""

import lightgbm as lgb
import numpy as np
import pandas as pd

from . import config
from .features import FEATURES, TARGET

PARAMS = {
    "objective": "l1",          # optimises absolute error, robust to outliers
    "learning_rate": 0.03,
    "num_leaves": 63,
    "min_data_in_leaf": 40,
    "feature_fraction": 0.8,
    "bagging_fraction": 0.8,
    "bagging_freq": 1,
    "lambda_l2": 1.0,
    "seed": 42,
    "deterministic": True,
    "verbose": -1,
}


def _local(df: pd.DataFrame) -> pd.DatetimeIndex:
    return df.index.tz_convert(config.TZ)


def _trainable(df: pd.DataFrame) -> pd.DataFrame:
    return df[df[TARGET].notna() & df["load_lag336"].notna()]


def choose_rounds(
    df: pd.DataFrame, w: config.Window, max_rounds: int = 5000, feature_list: list[str] | None = None
) -> tuple[int, float]:
    """Pick the number of boosting rounds on the window's validation period.

    Training data ends one day before the validation period starts, for the
    same reason as in `rolling_lgbm`. Returns (best_rounds, validation MAPE %).
    """
    feats = feature_list or FEATURES
    loc = _local(df)
    train = _trainable(df[(loc >= config.HISTORY_START) & (loc < w.valid_start - pd.Timedelta(days=1))])
    valid = _trainable(df[(loc >= w.valid_start) & (loc < w.test_start)])

    model = lgb.train(
        PARAMS,
        lgb.Dataset(train[feats], train[TARGET]),
        num_boost_round=max_rounds,
        valid_sets=[lgb.Dataset(valid[feats], valid[TARGET])],
        callbacks=[lgb.early_stopping(200, verbose=False)],
    )
    pred = model.predict(valid[feats], num_iteration=model.best_iteration)
    mape = float(np.mean(np.abs(pred - valid[TARGET]) / valid[TARGET]) * 100)
    return model.best_iteration, mape


def rolling_lgbm(
    df: pd.DataFrame, rounds: int, w: config.Window, feature_list: list[str] | None = None
) -> tuple[pd.Series, lgb.Booster]:
    """Monthly expanding-window retraining over the window's test period.

    `feature_list` defaults to all features; the ablation study passes subsets.
    """
    feats = feature_list or FEATURES
    loc = _local(df)
    last = loc[df[TARGET].notna()].max()
    if w.test_end is not None:
        last = min(last, w.test_end - pd.Timedelta(hours=1))
    months = pd.date_range(w.test_start, last, freq="MS")

    preds = []
    model = None
    for m in months:
        # Forecasting the 1st of the month happens on the last day of the
        # previous month, when actuals up to the day before are known.
        cutoff = m - pd.Timedelta(days=1)
        train = _trainable(df[(loc >= config.HISTORY_START) & (loc < cutoff)])
        test = df[(loc >= m) & (loc < m + pd.offsets.MonthBegin(1))]
        model = lgb.train(PARAMS, lgb.Dataset(train[feats], train[TARGET]), num_boost_round=rounds)
        preds.append(pd.Series(model.predict(test[feats]), index=test.index))

    return pd.concat(preds).rename("lgbm"), model


def baselines(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {"naive_weekly": df["load_lag168"], "official": df["load_official"]},
        index=df.index,
    )
