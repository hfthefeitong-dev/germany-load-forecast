# Experiments

Everything here is decided on the validation periods; the test periods are looked at once, afterwards.

## 1. Upper bound: what if the inputs were perfect?

LightGBM trained before, and early-stopped on, each validation period. The cheat variants use
information a real day-ahead forecaster cannot have; the gain shows how much headroom each input has.

| window   | variant                                              |   validation MAPE % |   trees |
|:---------|:-----------------------------------------------------|--------------------:|--------:|
| main     | official forecast (reference)                        |                3.71 |     nan |
| main     | current: 48 h-ahead weather forecast, load up to D-2 |                2.26 |    3061 |
| main     | cheat: observed weather                              |                2.28 |    1164 |
| main     | cheat: load of the full day D-1                      |                1.92 |    2667 |
| main     | cheat: both                                          |                1.89 |    2373 |
| backtest | official forecast (reference)                        |                4.51 |     nan |
| backtest | current: 48 h-ahead weather forecast, load up to D-2 |                4.81 |     141 |
| backtest | cheat: observed weather                              |                4.7  |     144 |
| backtest | cheat: load of the full day D-1                      |                4.21 |     163 |
| backtest | cheat: both                                          |                4.27 |     149 |

## 2. Bias correction

Forecast for day D minus alpha times the mean error of the last `window_days` days known at
forecast time (up to D-2). Parameters chosen on validation:

| window   | model       |   window_days |   alpha | by_hour   |   valid MAPE before % |   valid MAPE after % |
|:---------|:------------|--------------:|--------:|:----------|----------------------:|---------------------:|
| main     | lgbm        |             7 |    0.5  | True      |                 2.313 |                2.236 |
| main     | chronos_cov |            14 |    0.25 | True      |                 2.156 |                2.161 |
| main     | ensemble    |             7 |    0.25 | True      |                 1.976 |                1.962 |
| main     | official    |            14 |    1    | True      |                 3.714 |                2.952 |
| backtest | lgbm        |             3 |    0.75 | True      |                 4.873 |                3.58  |
| backtest | chronos_cov |            14 |    0.25 | True      |                 3.467 |                3.45  |
| backtest | ensemble    |             7 |    0.75 | True      |                 3.716 |                3.301 |
| backtest | official    |             7 |    1    | True      |                 4.513 |                3.026 |

Test periods, parameters frozen (`+bc` = bias-corrected):

| window   | model                         |   test MAPE % |   months beating official |   months |   DM_stat |   p_value |
|:---------|:------------------------------|--------------:|--------------------------:|---------:|----------:|----------:|
| main     | lgbm                          |        2.969  |                         9 |       12 |  nan      |  nan      |
| main     | chronos_cov                   |        3.0066 |                        10 |       12 |  nan      |  nan      |
| main     | official                      |        3.8362 |                         0 |       12 |  nan      |  nan      |
| main     | ensemble                      |        2.6934 |                        12 |       12 |  nan      |  nan      |
| main     | lgbm+bc                       |        2.8993 |                        11 |       12 |  nan      |  nan      |
| main     | chronos_cov+bc                |        2.9996 |                        10 |       12 |  nan      |  nan      |
| main     | ensemble+bc                   |        2.6654 |                        12 |       12 |  nan      |  nan      |
| main     | official+bc                   |        3.4299 |                         9 |       12 |  nan      |  nan      |
| main     | DM ensemble+bc vs ensemble    |      nan      |                       nan |      nan |   -1.4784 |    0.1393 |
| main     | DM ensemble+bc vs official+bc |      nan      |                       nan |      nan |   -5.7537 |    0      |
| main     | DM official+bc vs official    |      nan      |                       nan |      nan |   -2.5999 |    0.0093 |
| backtest | lgbm                          |        3.3409 |                         6 |        9 |  nan      |  nan      |
| backtest | chronos_cov                   |        2.4606 |                         9 |        9 |  nan      |  nan      |
| backtest | official                      |        3.8255 |                         0 |        9 |  nan      |  nan      |
| backtest | ensemble                      |        2.5947 |                         9 |        9 |  nan      |  nan      |
| backtest | lgbm+bc                       |        3.2678 |                         6 |        9 |  nan      |  nan      |
| backtest | chronos_cov+bc                |        2.4576 |                         9 |        9 |  nan      |  nan      |
| backtest | ensemble+bc                   |        2.6637 |                         9 |        9 |  nan      |  nan      |
| backtest | official+bc                   |        2.8731 |                         9 |        9 |  nan      |  nan      |
| backtest | DM ensemble+bc vs ensemble    |      nan      |                       nan |      nan |    0.7173 |    0.4732 |
| backtest | DM ensemble+bc vs official+bc |      nan      |                       nan |      nan |   -1.2921 |    0.1963 |
| backtest | DM official+bc vs official    |      nan      |                       nan |      nan |   -5.7736 |    0      |
