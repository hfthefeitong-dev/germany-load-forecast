# PV and battery storage capacity

Monthly installed PV (GWp) and battery storage (GWh) from Energy-Charts (Fraunhofer ISE),
lagged by two months, turned into physics-motivated features: capacity x forecast radiation,
its change against the same hour last week, and battery capacity x daily radiation.
Decision rule, fixed in advance: a model adopts the features only if its validation MAPE
improves in both windows.

## Diagnostic: does the official forecast fall further behind the PV build-out?

Slope of the official forecast's midday error against forecast radiation, per year.

|   year | days                |   hours |   error slope, % per 100 W/m2 |
|-------:|:--------------------|--------:|------------------------------:|
|   2024 | working days        |    1659 |                          1.13 |
|   2024 | weekends & holidays |     767 |                          2.02 |
|   2025 | working days        |    1757 |                          1.37 |
|   2025 | weekends & holidays |     798 |                          1.89 |
|   2026 | working days        |    1281 |                          1.12 |
|   2026 | weekends & holidays |     581 |                          1.63 |

## Validation

| window   | model     |   valid MAPE before % |   valid MAPE with PV features % |
|:---------|:----------|----------------------:|--------------------------------:|
| main     | LightGBM  |                 2.3   |                           2.412 |
| main     | Chronos-2 |                 2.156 |                           2.205 |
| backtest | LightGBM  |                 4.729 |                           4.648 |
| backtest | Chronos-2 |                 3.467 |                           3.495 |

## Test periods, looked at once

| window   | model                        |   test MAPE % |   months beating official |   months beating official+bc |   months |   DM_stat |   p_value |
|:---------|:-----------------------------|--------------:|--------------------------:|-----------------------------:|---------:|----------:|----------:|
| main     | official                     |        3.8362 |                         0 |                            3 |       12 |  nan      |  nan      |
| main     | official+bc                  |        3.4299 |                         9 |                            0 |       12 |  nan      |  nan      |
| main     | lgbm                         |        2.995  |                         9 |                            9 |       12 |  nan      |  nan      |
| main     | lgbm_pv                      |        3.0863 |                         9 |                            9 |       12 |  nan      |  nan      |
| main     | chronos_cov                  |        3.0069 |                        10 |                            7 |       12 |  nan      |  nan      |
| main     | chronos_pv                   |        3.0811 |                        10 |                            7 |       12 |  nan      |  nan      |
| main     | ensemble                     |        2.6988 |                        12 |                           11 |       12 |  nan      |  nan      |
| main     | ensemble_pv                  |        2.8346 |                        10 |                           10 |       12 |  nan      |  nan      |
| main     | DM lgbm_pv vs lgbm           |      nan      |                       nan |                          nan |      nan |    1.4029 |    0.1606 |
| main     | DM chronos_pv vs chronos_cov |      nan      |                       nan |                          nan |      nan |    2.9666 |    0.003  |
| main     | DM ensemble_pv vs ensemble   |      nan      |                       nan |                          nan |      nan |    3.4324 |    0.0006 |
| backtest | official                     |        3.8255 |                         0 |                            0 |        9 |  nan      |  nan      |
| backtest | official+bc                  |        2.8731 |                         9 |                            0 |        9 |  nan      |  nan      |
| backtest | lgbm                         |        3.2628 |                         7 |                            4 |        9 |  nan      |  nan      |
| backtest | lgbm_pv                      |        3.2373 |                         7 |                            4 |        9 |  nan      |  nan      |
| backtest | chronos_cov                  |        2.4599 |                         9 |                            7 |        9 |  nan      |  nan      |
| backtest | chronos_pv                   |        2.5724 |                         9 |                            7 |        9 |  nan      |  nan      |
| backtest | ensemble                     |        2.5547 |                         9 |                            8 |        9 |  nan      |  nan      |
| backtest | ensemble_pv                  |        2.5955 |                         8 |                            7 |        9 |  nan      |  nan      |
| backtest | DM lgbm_pv vs lgbm           |      nan      |                       nan |                          nan |      nan |   -0.4058 |    0.6849 |
| backtest | DM chronos_pv vs chronos_cov |      nan      |                       nan |                          nan |      nan |    3.027  |    0.0025 |
| backtest | DM ensemble_pv vs ensemble   |      nan      |                       nan |                          nan |      nan |    1.2614 |    0.2072 |

## MAPE by situation, main test period

| segment               |   hours |   official |   official+bc |   lgbm |   lgbm_pv |   chronos_cov |   chronos_pv |   ensemble |   ensemble_pv |
|:----------------------|--------:|-----------:|--------------:|-------:|----------:|--------------:|-------------:|-----------:|--------------:|
| all hours             |    8616 |       3.84 |          3.43 |   2.99 |      3.09 |          3.01 |         3.08 |       2.7  |          2.83 |
| working days          |    5856 |       3.51 |          3.19 |   2.82 |      2.95 |          2.83 |         2.87 |       2.58 |          2.71 |
| weekends              |    2448 |       4.43 |          3.96 |   3.4  |      3.42 |          3.01 |         3.12 |       2.82 |          2.92 |
| public holidays       |     264 |       4.61 |          3.57 |   3.18 |      3.22 |          6.03 |         6.64 |       3.9  |          4.46 |
| bridge days           |      72 |       7.25 |          4.16 |   2.72 |      3.08 |          6.55 |         6.33 |       4.36 |          4.45 |
| Christmas period      |     216 |       4.79 |          4.46 |   3.43 |      4.22 |          7.16 |         7.45 |       4.71 |          5.67 |
| sunny off-day middays |     226 |       8.57 |          4.07 |   3.23 |      2.9  |          3.41 |         3.34 |       2.75 |          2.55 |

## LightGBM feature importance with PV features (last main-period model)

|                        |   share of gain % |
|:-----------------------|------------------:|
| load_lag168            |             25.31 |
| load_lag336            |             11.19 |
| temp_daymean           |              4.98 |
| doy_sin                |              4.92 |
| load_daymean_lag7      |              4.81 |
| hour                   |              4.48 |
| battery_evening_delta7 |              4.11 |
| load_lag48             |              4.04 |
| doy_cos                |              3.69 |
| load_daymean_lag2      |              3.63 |
| rad_daymean            |              3.38 |
| temp                   |              3.36 |
| cloud                  |              3.24 |
| battery_evening        |              2.97 |
| pv_potential_delta7    |              2.66 |
| dow                    |              1.98 |
| is_offday              |              1.73 |
| holiday_share          |              1.67 |
| pv_gw                  |              1.6  |
| rad                    |              1.17 |
| pv_potential_south     |              1.12 |
| rad_south              |              1.09 |
| pv_potential           |              1.06 |
| holiday_share_lag7     |              0.5  |
| bridge                 |              0.46 |
| battery_gwh            |              0.38 |
| holiday_share_lag2     |              0.26 |
| xmas                   |              0.22 |
