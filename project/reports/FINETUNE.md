# Fine-tuning Chronos-2

Decision rule, fixed in advance: fine-tuning counts only if it beats zero-shot Chronos-2 on the
validation period of both windows. Selection fine-tunes on data before the validation period;
the test model is fine-tuned once on data before the test period and not refreshed.

## Selection on validation

| window   | finetune_mode   |   learning_rate |   num_steps |   inference context h |   valid MAPE % |   zero-shot valid MAPE % |
|:---------|:----------------|----------------:|------------:|----------------------:|---------------:|-------------------------:|
| main     | lora            |           1e-05 |         500 |                  2048 |          2.024 |                    2.156 |
| main     | lora            |           1e-05 |         500 |                  8192 |          2.214 |                    2.156 |
| main     | lora            |           1e-05 |        2000 |                  2048 |          2.076 |                    2.156 |
| main     | lora            |           1e-05 |        2000 |                  8192 |          2.355 |                    2.156 |
| main     | full            |           1e-06 |         500 |                  2048 |          2.146 |                    2.156 |
| main     | full            |           1e-06 |         500 |                  8192 |          2.148 |                    2.156 |
| main     | full            |           1e-06 |        2000 |                  2048 |          2.061 |                    2.156 |
| main     | full            |           1e-06 |        2000 |                  8192 |          2.39  |                    2.156 |
| backtest | lora            |           1e-05 |         500 |                  2048 |          3.622 |                    3.467 |
| backtest | lora            |           1e-05 |         500 |                  8192 |          3.574 |                    3.467 |
| backtest | lora            |           1e-05 |        2000 |                  2048 |          4.101 |                    3.467 |
| backtest | lora            |           1e-05 |        2000 |                  8192 |          3.957 |                    3.467 |
| backtest | full            |           1e-06 |         500 |                  2048 |          3.799 |                    3.467 |
| backtest | full            |           1e-06 |         500 |                  8192 |          3.552 |                    3.467 |
| backtest | full            |           1e-06 |        2000 |                  2048 |          3.726 |                    3.467 |
| backtest | full            |           1e-06 |        2000 |                  8192 |          3.61  |                    3.467 |

## Test periods, looked at once

| window   | model                                                                                                 |   test MAPE % |   months beating official |   months beating official+bc |   months |   DM_stat |   p_value |
|:---------|:------------------------------------------------------------------------------------------------------|--------------:|--------------------------:|-----------------------------:|---------:|----------:|----------:|
| main     | official                                                                                              |        3.8362 |                         0 |                            3 |       12 |  nan      |  nan      |
| main     | official+bc                                                                                           |        3.4299 |                         9 |                            0 |       12 |  nan      |  nan      |
| main     | chronos_cov                                                                                           |        3.0069 |                        10 |                            7 |       12 |  nan      |  nan      |
| main     | chronos_ft                                                                                            |        2.6633 |                        11 |                           11 |       12 |  nan      |  nan      |
| main     | ensemble                                                                                              |        2.6988 |                        12 |                           11 |       12 |  nan      |  nan      |
| main     | ensemble_ft                                                                                           |        2.5887 |                        12 |                           11 |       12 |  nan      |  nan      |
| main     | ensemble_morning                                                                                      |        2.6387 |                        12 |                           12 |       12 |  nan      |  nan      |
| main     | ensemble_ft_morning                                                                                   |        2.5331 |                        12 |                           12 |       12 |  nan      |  nan      |
| main     | DM chronos_ft vs chronos_cov                                                                          |      nan      |                       nan |                          nan |      nan |   -3.6867 |    0.0002 |
| main     | DM ensemble_ft vs ensemble                                                                            |      nan      |                       nan |                          nan |      nan |   -2.6081 |    0.0091 |
| main     | DM ensemble_ft_morning vs ensemble_morning                                                            |      nan      |                       nan |                          nan |      nan |   -3.041  |    0.0024 |
| main     | DM ensemble_ft_morning vs official+bc                                                                 |      nan      |                       nan |                          nan |      nan |   -6.1609 |    0      |
| main     | chosen: {'finetune_mode': 'lora', 'learning_rate': 1e-05, 'num_steps': 500}, inference context 2048 h |      nan      |                       nan |                          nan |      nan |  nan      |  nan      |
| backtest | official                                                                                              |        3.8255 |                         0 |                            0 |        9 |  nan      |  nan      |
| backtest | official+bc                                                                                           |        2.8731 |                         9 |                            0 |        9 |  nan      |  nan      |
| backtest | chronos_cov                                                                                           |        2.4599 |                         9 |                            7 |        9 |  nan      |  nan      |
| backtest | chronos_ft                                                                                            |        2.4717 |                         9 |                            8 |        9 |  nan      |  nan      |
| backtest | ensemble                                                                                              |        2.5547 |                         9 |                            8 |        9 |  nan      |  nan      |
| backtest | ensemble_ft                                                                                           |        2.5717 |                         9 |                            7 |        9 |  nan      |  nan      |
| backtest | ensemble_morning                                                                                      |        2.4252 |                         9 |                            8 |        9 |  nan      |  nan      |
| backtest | ensemble_ft_morning                                                                                   |        2.4517 |                         9 |                            8 |        9 |  nan      |  nan      |
| backtest | DM chronos_ft vs chronos_cov                                                                          |      nan      |                       nan |                          nan |      nan |    0.0802 |    0.9361 |
| backtest | DM ensemble_ft vs ensemble                                                                            |      nan      |                       nan |                          nan |      nan |    0.6205 |    0.5349 |
| backtest | DM ensemble_ft_morning vs ensemble_morning                                                            |      nan      |                       nan |                          nan |      nan |    0.6792 |    0.497  |
| backtest | DM ensemble_ft_morning vs official+bc                                                                 |      nan      |                       nan |                          nan |      nan |   -2.9082 |    0.0036 |
| backtest | chosen: {'finetune_mode': 'full', 'learning_rate': 1e-06, 'num_steps': 500}, inference context 8192 h |      nan      |                       nan |                          nan |      nan |  nan      |  nan      |

## MAPE by situation, main test period

| segment               |   hours |   official |   official+bc |   chronos_cov |   chronos_ft |   ensemble |   ensemble_ft |   ensemble_morning |   ensemble_ft_morning |
|:----------------------|--------:|-----------:|--------------:|--------------:|-------------:|-----------:|--------------:|-------------------:|----------------------:|
| all hours             |    8616 |       3.84 |          3.43 |          3.01 |         2.66 |       2.7  |          2.59 |               2.64 |                  2.53 |
| working days          |    5856 |       3.51 |          3.19 |          2.83 |         2.56 |       2.58 |          2.46 |               2.51 |                  2.42 |
| weekends              |    2448 |       4.43 |          3.96 |          3.01 |         2.67 |       2.82 |          2.78 |               2.79 |                  2.71 |
| public holidays       |     264 |       4.61 |          3.57 |          6.03 |         4.53 |       3.9  |          3.43 |               3.75 |                  3.4  |
| bridge days           |      72 |       7.25 |          4.16 |          6.55 |         5.33 |       4.36 |          3.61 |               4.38 |                  3.18 |
| Christmas period      |     216 |       4.79 |          4.46 |          7.16 |         4.22 |       4.71 |          3.44 |               3.9  |                  3.4  |
| sunny off-day middays |     226 |       8.57 |          4.07 |          3.41 |         2.45 |       2.75 |          2.56 |               2.89 |                  2.76 |
