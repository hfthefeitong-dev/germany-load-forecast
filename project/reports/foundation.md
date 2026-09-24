## Overall

|              |   MAPE_% |   MAE_MW |   RMSE_MW |   bias_MW |   hours |
|:-------------|---------:|---------:|----------:|----------:|--------:|
| naive_weekly |     5.53 |  2936.48 |   4211.27 |     26.31 |    8610 |
| official     |     3.84 |  2032.21 |   2617.04 |    233.16 |    8610 |
| lgbm         |     2.97 |  1579.42 |   1991.29 |   -157.8  |    8610 |
| chronos_uni  |     3.58 |  1884.1  |   2725.17 |    -64.81 |    8610 |
| chronos_cov  |     3    |  1585.9  |   2120.22 |     -5.53 |    8610 |

## MAPE by situation [%]

| segment               |   hours |   naive_weekly |   official |   lgbm |   chronos_uni |   chronos_cov |
|:----------------------|--------:|---------------:|-----------:|-------:|--------------:|--------------:|
| all hours             |    8610 |           5.53 |       3.84 |   2.97 |          3.58 |          3    |
| working days          |    5850 |           5.03 |       3.51 |   2.81 |          3.06 |          2.79 |
| weekends              |    2448 |           4.99 |       4.43 |   3.36 |          3.35 |          2.97 |
| public holidays       |     264 |          20.5  |       4.61 |   3.1  |         16.35 |          7.32 |
| bridge days           |      72 |          10.38 |       7.25 |   2.66 |          7.96 |          6.07 |
| Christmas period      |     216 |           9.67 |       4.79 |   3.54 |          9.12 |          7.21 |
| sunny off-day middays |     226 |           8.19 |       8.57 |   3.16 |          6.01 |          3.04 |

## Diebold-Mariano, LightGBM vs Chronos-2 with covariates

{
  "days": 359,
  "mean_daily_MAE_diff_MW": -6.1893285133554095,
  "DM_stat": -0.07372226078177199,
  "p_value": 0.9412313854431611
}
