# Live forecasts

On-time live forecasts with known actuals: 52 days. The pre-registered evaluation
(live/PREREGISTRATION.md) happens after at least 60 days.

## Point forecasts

| model               |   hours |   MAPE % |
|:--------------------|--------:|---------:|
| official            |    1235 |     3.57 |
| official+bc         |    1235 |     3.07 |
| lgbm                |    1235 |     2.64 |
| chronos             |    1235 |     2.58 |
| ensemble            |    1235 |     2.41 |
| lgbm_morning        |    1187 |     2.14 |
| chronos_morning     |    1187 |     2.32 |
| ensemble_morning    |    1187 |     2.07 |
| chronos_ft          |    1235 |     2.25 |
| ensemble_ft         |    1235 |     2.28 |
| ensemble_ft_morning |    1187 |     1.99 |

## Probabilistic forecasts

| method                               |   mean pinball MW |   coverage 80 % (P10-P90) |   coverage 90 % (P5-P95) |   width 80 % MW |   median MAPE % |   hours |
|:-------------------------------------|------------------:|--------------------------:|-------------------------:|----------------:|----------------:|--------:|
| avg(LightGBM + conformal, Chronos-2) |            388.76 |                     79.19 |                    86.88 |         4131.06 |            2.36 |    1235 |
| official + conformal (benchmark)     |            505.43 |                     70.85 |                    80.89 |         4315.34 |            2.99 |    1235 |
