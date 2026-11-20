# Live forecasts

On-time live forecasts with known actuals: 46 days. The pre-registered evaluation
(live/PREREGISTRATION.md) happens after at least 60 days.

## Point forecasts

| model               |   hours |   MAPE % |
|:--------------------|--------:|---------:|
| official            |    1092 |     3.41 |
| official+bc         |    1092 |     2.95 |
| lgbm                |    1092 |     2.5  |
| chronos             |    1092 |     2.49 |
| ensemble            |    1092 |     2.3  |
| lgbm_morning        |    1092 |     2.17 |
| chronos_morning     |    1092 |     2.33 |
| ensemble_morning    |    1092 |     2.08 |
| chronos_ft          |    1092 |     2.32 |
| ensemble_ft         |    1092 |     2.23 |
| ensemble_ft_morning |    1092 |     2.03 |

## Probabilistic forecasts

| method                               |   mean pinball MW |   coverage 80 % (P10-P90) |   coverage 90 % (P5-P95) |   width 80 % MW |   median MAPE % |   hours |
|:-------------------------------------|------------------:|--------------------------:|-------------------------:|----------------:|----------------:|--------:|
| avg(LightGBM + conformal, Chronos-2) |            357.66 |                     82.05 |                    89.38 |         4110.1  |            2.24 |    1092 |
| official + conformal (benchmark)     |            483.36 |                     73.17 |                    83.06 |         4291.92 |            2.9  |    1092 |
