# Live forecasts

On-time live forecasts with known actuals: 13 days. The pre-registered evaluation
(live/PREREGISTRATION.md) happens after at least 60 days.

## Point forecasts

| model               |   hours |   MAPE % |
|:--------------------|--------:|---------:|
| official            |     298 |     3.56 |
| official+bc         |     298 |     3.59 |
| lgbm                |     298 |     2.94 |
| chronos             |     298 |     3.16 |
| ensemble            |     298 |     2.81 |
| lgbm_morning        |     298 |     2.37 |
| chronos_morning     |     298 |     3.14 |
| ensemble_morning    |     298 |     2.56 |
| chronos_ft          |     298 |     2.57 |
| ensemble_ft         |     298 |     2.59 |
| ensemble_ft_morning |     298 |     2.21 |

## Probabilistic forecasts

| method                               |   mean pinball MW |   coverage 80 % (P10-P90) |   coverage 90 % (P5-P95) |   width 80 % MW |   median MAPE % |   hours |
|:-------------------------------------|------------------:|--------------------------:|-------------------------:|----------------:|----------------:|--------:|
| avg(LightGBM + conformal, Chronos-2) |            385.64 |                     78.86 |                    86.24 |         4246.73 |            2.58 |     298 |
| official + conformal (benchmark)     |            567.32 |                     72.15 |                    76.51 |         4185.92 |            3.39 |     298 |
