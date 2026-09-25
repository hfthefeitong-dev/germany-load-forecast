# Probabilistic forecasts

Quantiles P5, P10, P25, P50, P75, P90, P95. Mean pinball loss (lower is better) rewards forecasts
that are sharp and honest; coverage shows whether an 80 % or 90 % interval really contains the
actual value that often. Look-back windows and the choice of method are made on validation.

## Selection on validation

| window   | method                               |   look-back days |   valid mean pinball MW |
|:---------|:-------------------------------------|-----------------:|------------------------:|
| main     | lgbm+conformal                       |               14 |                  378.97 |
| main     | lgbm+conformal                       |               28 |                  358.61 |
| main     | lgbm+conformal                       |               42 |                  360.54 |
| main     | ensemble+conformal                   |               14 |                  327.52 |
| main     | ensemble+conformal                   |               28 |                  311.4  |
| main     | ensemble+conformal                   |               42 |                  312.51 |
| main     | official+conformal                   |               14 |                  447.62 |
| main     | official+conformal                   |               28 |                  430.74 |
| main     | official+conformal                   |               42 |                  416.22 |
| main     | chronos (native)                     |              nan |                  323.1  |
| main     | avg(lgbm+conformal, chronos)         |              nan |                  303.36 |
| main     | CHOSEN: avg(lgbm+conformal, chronos) |              nan |                  303.36 |
| backtest | lgbm+conformal                       |               14 |                  805.6  |
| backtest | lgbm+conformal                       |               28 |                  981.12 |
| backtest | lgbm+conformal                       |               42 |                 1064.8  |
| backtest | ensemble+conformal                   |               14 |                  685.93 |
| backtest | ensemble+conformal                   |               28 |                  749.8  |
| backtest | ensemble+conformal                   |               42 |                  794.58 |
| backtest | official+conformal                   |               14 |                  590.18 |
| backtest | official+conformal                   |               28 |                  678.32 |
| backtest | official+conformal                   |               42 |                  766.08 |
| backtest | chronos (native)                     |              nan |                  671.18 |
| backtest | avg(lgbm+conformal, chronos)         |              nan |                  663.97 |
| backtest | CHOSEN: avg(lgbm+conformal, chronos) |              nan |                  663.97 |

## Test periods, looked at once

| window   | method                                                            |   mean pinball MW |   coverage 80 % (P10-P90) |   coverage 90 % (P5-P95) |   width 80 % MW |   median MAPE % |   hours |   skill vs benchmark % |   DM_stat |   p_value |
|:---------|:------------------------------------------------------------------|------------------:|--------------------------:|-------------------------:|----------------:|----------------:|--------:|-----------------------:|----------:|----------:|
| main     | official+conformal (benchmark)                                    |            546.88 |                     74.2  |                    82.74 |         5391.65 |            3.53 |    8610 |                   0    |     nan   |    nan    |
| main     | lgbm+conformal                                                    |            477.96 |                     73.1  |                    82.21 |         4513.53 |            3.13 |    8610 |                  12.6  |     nan   |    nan    |
| main     | ensemble+conformal                                                |            437.62 |                     73.19 |                    82.59 |         4149.84 |            2.84 |    8610 |                  19.98 |     nan   |    nan    |
| main     | chronos (native)                                                  |            460.03 |                     77.56 |                    89    |         4932.43 |            3.01 |    8610 |                  15.88 |     nan   |    nan    |
| main     | avg(lgbm+conformal, chronos) <- chosen                            |            419.41 |                     80.07 |                    90.02 |         4722.98 |            2.79 |    8610 |                  23.31 |     nan   |    nan    |
| main     | DM avg(lgbm+conformal, chronos) vs benchmark (daily mean pinball) |            nan    |                    nan    |                   nan    |          nan    |          nan    |     nan |                 nan    |      -5.8 |      0    |
| backtest | official+conformal (benchmark)                                    |            439.27 |                     66.74 |                    76.31 |         3754.38 |            2.87 |    6551 |                   0    |     nan   |    nan    |
| backtest | lgbm+conformal                                                    |            579.15 |                     65.59 |                    74.66 |         4397.46 |            3.57 |    6551 |                 -31.85 |     nan   |    nan    |
| backtest | ensemble+conformal                                                |            444.77 |                     66.81 |                    76.37 |         3670.62 |            2.75 |    6551 |                  -1.25 |     nan   |    nan    |
| backtest | chronos (native)                                                  |            374.62 |                     81.1  |                    91.6  |         4374.72 |            2.46 |    6551 |                  14.72 |     nan   |    nan    |
| backtest | avg(lgbm+conformal, chronos) <- chosen                            |            416.23 |                     78.11 |                    87.79 |         4386.09 |            2.72 |    6551 |                   5.24 |     nan   |    nan    |
| backtest | DM avg(lgbm+conformal, chronos) vs benchmark (daily mean pinball) |            nan    |                    nan    |                   nan    |          nan    |          nan    |     nan |                 nan    |      -0.7 |      0.48 |

## Reliability: share of actual values below each quantile (ideal = the quantile level)

| window   | method                         |   share below P5 % |   share below P10 % |   share below P25 % |   share below P50 % |   share below P75 % |   share below P90 % |   share below P95 % |
|:---------|:-------------------------------|-------------------:|--------------------:|--------------------:|--------------------:|--------------------:|--------------------:|--------------------:|
| main     | official+conformal (benchmark) |                7.8 |                11.9 |                26   |                47.7 |                70.9 |                86.1 |                90.5 |
| main     | avg(lgbm+conformal, chronos)   |                4.7 |                 9.4 |                25.6 |                50.9 |                74.8 |                89.5 |                94.8 |
| backtest | official+conformal (benchmark) |               11.7 |                16.8 |                31.2 |                52   |                71.6 |                83.5 |                88   |
| backtest | avg(lgbm+conformal, chronos)   |                5.1 |                10.4 |                25.7 |                51.4 |                74.9 |                88.6 |                92.8 |
