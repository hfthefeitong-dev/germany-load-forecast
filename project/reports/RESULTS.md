# Results

Test period: 2025-10-01 to 2026-09-24, 8610 hours.

## Overall

|              |   MAPE_% |   MAE_MW |   RMSE_MW |   bias_MW |   hours |
|:-------------|---------:|---------:|----------:|----------:|--------:|
| naive_weekly |     5.53 |  2936.48 |   4211.27 |     26.31 |    8610 |
| official     |     3.84 |  2032.21 |   2617.04 |    233.16 |    8610 |
| lgbm         |     2.97 |  1579.42 |   1991.29 |   -157.8  |    8610 |
| chronos_uni  |     3.58 |  1884.1  |   2725.17 |    -64.81 |    8610 |
| chronos_cov  |     3    |  1585.9  |   2120.22 |     -5.53 |    8610 |
| ensemble     |     2.68 |  1422.67 |   1826.77 |    -81.66 |    8610 |

## MAPE by situation [%]

| segment               |   hours |   naive_weekly |   official |   lgbm |   chronos_uni |   chronos_cov |   ensemble |
|:----------------------|--------:|---------------:|-----------:|-------:|--------------:|--------------:|-----------:|
| all hours             |    8610 |           5.53 |       3.84 |   2.97 |          3.58 |          3    |       2.68 |
| working days          |    5850 |           5.03 |       3.51 |   2.81 |          3.06 |          2.79 |       2.55 |
| weekends              |    2448 |           4.99 |       4.43 |   3.36 |          3.35 |          2.97 |       2.78 |
| public holidays       |     264 |          20.5  |       4.61 |   3.1  |         16.35 |          7.32 |       4.4  |
| bridge days           |      72 |          10.38 |       7.25 |   2.66 |          7.96 |          6.07 |       4.16 |
| Christmas period      |     216 |           9.67 |       4.79 |   3.54 |          9.12 |          7.21 |       4.79 |
| sunny off-day middays |     226 |           8.19 |       8.57 |   3.16 |          6.01 |          3.04 |       2.47 |

## Diebold-Mariano tests (daily MAE, Newey-West, 7 lags; negative = first model better)

|                         |   days |   mean_daily_MAE_diff_MW |   DM_stat |   p_value |
|:------------------------|-------:|-------------------------:|----------:|----------:|
| lgbm vs official        |    359 |                 -452.559 |   -5.5347 |    0      |
| chronos_cov vs official |    359 |                 -446.37  |   -4.4403 |    0      |
| ensemble vs official    |    359 |                 -609.646 |   -7.2492 |    0      |
| ensemble vs lgbm        |    359 |                 -157.087 |   -3.857  |    0.0001 |

## Extra imbalance cost (whole of Germany as one balancing group, a thought experiment)

| model        |   extra_cost_mEUR |   EUR_per_MWh |   hours |
|:-------------|------------------:|--------------:|--------:|
| naive_weekly |            454.1  |          1.05 |    8040 |
| official     |            144.95 |          0.33 |    8040 |
| lgbm         |             91.09 |          0.21 |    8040 |
| chronos_uni  |            203.97 |          0.47 |    8040 |
| chronos_cov  |            101.77 |          0.23 |    8040 |
| ensemble     |             96.43 |          0.22 |    8040 |

### Same, excluding hours with |reBAP| > 1000 EUR/MWh

| model        |   extra_cost_mEUR |   EUR_per_MWh |   hours |
|:-------------|------------------:|--------------:|--------:|
| naive_weekly |            287.36 |          0.66 |    8027 |
| official     |             81.93 |          0.19 |    8027 |
| lgbm         |             74.11 |          0.17 |    8027 |
| chronos_uni  |            110.89 |          0.26 |    8027 |
| chronos_cov  |             86.47 |          0.2  |    8027 |
| ensemble     |             80.29 |          0.19 |    8027 |
