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


def choose_rounds(df: pd.DataFrame, max_rounds: int = 5000) -> tuple[int, float]:
    """Pick the number of boosting rounds on a validation window *before* the test set.

    Returns (best_rounds, validation MAPE in %).
    """
    loc = _local(df)
    train = _trainable(df[(loc >= config.HISTORY_START) & (loc < config.VALID_START - pd.Timedelta(days=1))])
    valid = _trainable(df[(loc >= config.VALID_START) & (loc < config.TEST_START)])

    model = lgb.train(
        PARAMS,
        lgb.Dataset(train[FEATURES], train[TARGET]),
        num_boost_round=max_rounds,
        valid_sets=[lgb.Dataset(valid[FEATURES], valid[TARGET])],
        callbacks=[lgb.early_stopping(200, verbose=False)],
    )
    pred = model.predict(valid[FEATURES], num_iteration=model.best_iteration)
    mape = float(np.mean(np.abs(pred - valid[TARGET]) / valid[TARGET]) * 100)
    return model.best_iteration, mape


def rolling_lgbm(
    df: pd.DataFrame, rounds: int, feature_list: list[str] | None = None
) -> tuple[pd.Series, lgb.Booster]:
    """Monthly expanding-window retraining over the test period.

    `feature_list` defaults to all features; the ablation study passes subsets.
    """
    feats = feature_list or FEATURES
    loc = _local(df)
    last = loc[df[TARGET].notna()].max()
    months = pd.date_range(config.TEST_START, last, freq="MS")

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
