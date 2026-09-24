# Experiments

Everything here is decided on the validation periods; the test periods are looked at once, afterwards.

## 1. Upper bound: what if the inputs were perfect?

LightGBM trained before, and early-stopped on, each validation period. The cheat variants use
information a real day-ahead forecaster cannot have; the gain shows how much headroom each input has.

| window   | variant                                              |   validation MAPE % |   trees |
|:---------|:-----------------------------------------------------|--------------------:|--------:|
| main     | official forecast (reference)                        |                3.71 |     nan |
| main     | current: 48 h-ahead weather forecast, load up to D-2 |                2.3  |    2122 |
| main     | cheat: observed weather                              |                2.35 |     457 |
| main     | cheat: load of the full day D-1                      |                1.95 |    1883 |
| main     | cheat: both                                          |                1.94 |     931 |
| backtest | official forecast (reference)                        |                4.51 |     nan |
| backtest | current: 48 h-ahead weather forecast, load up to D-2 |                4.73 |     155 |
| backtest | cheat: observed weather                              |                4.66 |     152 |
| backtest | cheat: load of the full day D-1                      |                4.2  |     148 |
| backtest | cheat: both                                          |                4.15 |     144 |

## 2. Bias correction

Forecast for day D minus alpha times the mean error of the last `window_days` days known at
forecast time (up to D-2). Parameters chosen on validation:

| window   | model       |   window_days |   alpha | by_hour   |   valid MAPE before % |   valid MAPE after % |
|:---------|:------------|--------------:|--------:|:----------|----------------------:|---------------------:|
| main     | lgbm        |             7 |    0.5  | True      |                 2.312 |                2.247 |
| main     | chronos_cov |            14 |    0.25 | True      |                 2.156 |                2.161 |
| main     | ensemble    |             7 |    0.25 | True      |                 1.977 |                1.969 |
| main     | official    |            14 |    1    | True      |                 3.714 |                2.952 |
| backtest | lgbm        |             3 |    0.75 | True      |                 4.85  |                3.54  |
| backtest | chronos_cov |            14 |    0.25 | True      |                 3.467 |                3.451 |
| backtest | ensemble    |             7 |    0.75 | True      |                 3.69  |                3.267 |
| backtest | official    |             7 |    1    | True      |                 4.513 |                3.026 |

Test periods, parameters frozen (`+bc` = bias-corrected):

| window   | model                         |   test MAPE % |   months beating official |   months beating official+bc |   months |   DM_stat |   p_value |
|:---------|:------------------------------|--------------:|--------------------------:|-----------------------------:|---------:|----------:|----------:|
| main     | lgbm                          |        2.995  |                         9 |                            9 |       12 |  nan      |  nan      |
| main     | chronos_cov                   |        3.0069 |                        10 |                            7 |       12 |  nan      |  nan      |
| main     | official                      |        3.8362 |                         0 |                            3 |       12 |  nan      |  nan      |
| main     | ensemble                      |        2.6988 |                        12 |                           11 |       12 |  nan      |  nan      |
| main     | lgbm+bc                       |        2.9134 |                        11 |                           10 |       12 |  nan      |  nan      |
| main     | chronos_cov+bc                |        3      |                        10 |                            7 |       12 |  nan      |  nan      |
| main     | ensemble+bc                   |        2.6613 |                        12 |                           12 |       12 |  nan      |  nan      |
| main     | official+bc                   |        3.4299 |                         9 |                            0 |       12 |  nan      |  nan      |
| main     | DM ensemble+bc vs ensemble    |      nan      |                       nan |                          nan |      nan |   -1.8572 |    0.0633 |
| main     | DM ensemble+bc vs official+bc |      nan      |                       nan |                          nan |      nan |   -5.7746 |    0      |
| main     | DM official+bc vs official    |      nan      |                       nan |                          nan |      nan |   -2.5999 |    0.0093 |
| backtest | lgbm                          |        3.2628 |                         7 |                            4 |        9 |  nan      |  nan      |
| backtest | chronos_cov                   |        2.4599 |                         9 |                            7 |        9 |  nan      |  nan      |
| backtest | official                      |        3.8255 |                         0 |                            0 |        9 |  nan      |  nan      |
| backtest | ensemble                      |        2.5547 |                         9 |                            8 |        9 |  nan      |  nan      |
| backtest | lgbm+bc                       |        3.2203 |                         6 |                            2 |        9 |  nan      |  nan      |
| backtest | chronos_cov+bc                |        2.457  |                         9 |                            7 |        9 |  nan      |  nan      |
| backtest | ensemble+bc                   |        2.6345 |                         9 |                            7 |        9 |  nan      |  nan      |
| backtest | official+bc                   |        2.8731 |                         9 |                            0 |        9 |  nan      |  nan      |
| backtest | DM ensemble+bc vs ensemble    |      nan      |                       nan |                          nan |      nan |    0.8213 |    0.4115 |
| backtest | DM ensemble+bc vs official+bc |      nan      |                       nan |                          nan |      nan |   -1.4307 |    0.1525 |
| backtest | DM official+bc vs official    |      nan      |                       nan |                          nan |      nan |   -5.7736 |    0      |

## 3. Fresher load: day D-1 until 08:00

Assumes the forecast is issued on D-1 at 10:00, before the day-ahead gate closure (12:00) and
the official forecast (18:00). SMARD publishes actual load with about 1 h delay (measured once,
2026-09-24), so load up to 07:59 is treated as known. Decision rule, fixed in advance: adopt only
if validation MAPE improves in both windows for both models.

| window   | model     |   valid MAPE, load up to D-2 % |   valid MAPE, + D-1 until 08:00 % |
|:---------|:----------|-------------------------------:|----------------------------------:|
| main     | LightGBM  |                          2.3   |                             2.196 |
| main     | Chronos-2 |                          2.156 |                             2.015 |
| backtest | LightGBM  |                          4.729 |                             4.065 |
| backtest | Chronos-2 |                          3.467 |                             2.876 |

Test periods, looked at once:

| window   | model                              |   test MAPE % |   months beating official |   months beating official+bc |   months |   DM_stat |   p_value |
|:---------|:-----------------------------------|--------------:|--------------------------:|-----------------------------:|---------:|----------:|----------:|
| main     | official                           |        3.8362 |                         0 |                            3 |       12 |  nan      |  nan      |
| main     | official+bc                        |        3.4299 |                         9 |                            0 |       12 |  nan      |  nan      |
| main     | ensemble                           |        2.6988 |                        12 |                           11 |       12 |  nan      |  nan      |
| main     | lgbm_morning                       |        2.9254 |                        11 |                           10 |       12 |  nan      |  nan      |
| main     | chronos_morning                    |        2.8268 |                        11 |                            9 |       12 |  nan      |  nan      |
| main     | ensemble_morning                   |        2.6387 |                        12 |                           12 |       12 |  nan      |  nan      |
| main     | DM ensemble_morning vs ensemble    |      nan      |                       nan |                          nan |      nan |   -1.4555 |    0.1455 |
| main     | DM ensemble_morning vs official+bc |      nan      |                       nan |                          nan |      nan |   -5.8625 |    0      |
| backtest | official                           |        3.8255 |                         0 |                            0 |        9 |  nan      |  nan      |
| backtest | official+bc                        |        2.8731 |                         9 |                            0 |        9 |  nan      |  nan      |
| backtest | ensemble                           |        2.5547 |                         9 |                            8 |        9 |  nan      |  nan      |
| backtest | lgbm_morning                       |        2.982  |                         7 |                            5 |        9 |  nan      |  nan      |
| backtest | chronos_morning                    |        2.387  |                         9 |                            8 |        9 |  nan      |  nan      |
| backtest | ensemble_morning                   |        2.4252 |                         9 |                            8 |        9 |  nan      |  nan      |
| backtest | DM ensemble_morning vs ensemble    |      nan      |                       nan |                          nan |      nan |   -1.8472 |    0.0647 |
| backtest | DM ensemble_morning vs official+bc |      nan      |                       nan |                          nan |      nan |   -3.0316 |    0.0024 |

MAPE by situation, main test period:

| segment               |   hours |   official |   official+bc |   ensemble |   lgbm_morning |   chronos_morning |   ensemble_morning |
|:----------------------|--------:|-----------:|--------------:|-----------:|---------------:|------------------:|-------------------:|
| all hours             |    8616 |       3.84 |          3.43 |       2.7  |           2.93 |              2.83 |               2.64 |
| working days          |    5856 |       3.51 |          3.19 |       2.58 |           2.84 |              2.61 |               2.51 |
| weekends              |    2448 |       4.43 |          3.96 |       2.82 |           3.12 |              2.96 |               2.79 |
| public holidays       |     264 |       4.61 |          3.57 |       3.9  |           3.12 |              5.41 |               3.75 |
| bridge days           |      72 |       7.25 |          4.16 |       4.36 |           2.56 |              6.53 |               4.38 |
| Christmas period      |     216 |       4.79 |          4.46 |       4.71 |           3.48 |              4.68 |               3.9  |
| sunny off-day middays |     226 |       8.57 |          4.07 |       2.75 |           3.47 |              3.3  |               2.89 |
