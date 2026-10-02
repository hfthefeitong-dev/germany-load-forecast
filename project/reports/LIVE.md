# Live forecasts

On-time live forecasts with known actuals: 1 days. The pre-registered evaluation
(live/PREREGISTRATION.md) happens after at least 60 days.

## Point forecasts

| model               |   hours |   MAPE % |
|:--------------------|--------:|---------:|
| official            |      10 |     8.2  |
| official+bc         |      10 |     7.39 |
| lgbm                |      10 |     4.32 |
| chronos             |      10 |     5.59 |
| ensemble            |      10 |     4.78 |
| lgbm_morning        |      10 |     4.29 |
| chronos_morning     |      10 |     5.06 |
| ensemble_morning    |      10 |     4.67 |
| chronos_ft          |      10 |     6.17 |
| ensemble_ft         |      10 |     5    |
| ensemble_ft_morning |      10 |     5.3  |

## Probabilistic forecasts

| method                               |   mean pinball MW |   coverage 80 % (P10-P90) |   coverage 90 % (P5-P95) |   width 80 % MW |   median MAPE % |   hours |
|:-------------------------------------|------------------:|--------------------------:|-------------------------:|----------------:|----------------:|--------:|
| avg(LightGBM + conformal, Chronos-2) |            588.31 |                        40 |                       50 |         3572.38 |            3.94 |      10 |
| official + conformal (benchmark)     |           1422.16 |                        10 |                       20 |         4026.88 |            7.39 |      10 |
