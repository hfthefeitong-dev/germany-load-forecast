# Live forecasts

On-time live forecasts with known actuals: 38 days. The pre-registered evaluation
(live/PREREGISTRATION.md) happens after at least 60 days.

## Point forecasts

| model               |   hours |   MAPE % |
|:--------------------|--------:|---------:|
| official            |     897 |     3.48 |
| official+bc         |     897 |     2.75 |
| lgbm                |     897 |     2.52 |
| chronos             |     897 |     2.63 |
| ensemble            |     897 |     2.36 |
| lgbm_morning        |     897 |     2.24 |
| chronos_morning     |     897 |     2.44 |
| ensemble_morning    |     897 |     2.16 |
| chronos_ft          |     897 |     2.31 |
| ensemble_ft         |     897 |     2.25 |
| ensemble_ft_morning |     897 |     2.06 |

## Probabilistic forecasts

| method                               |   mean pinball MW |   coverage 80 % (P10-P90) |   coverage 90 % (P5-P95) |   width 80 % MW |   median MAPE % |   hours |
|:-------------------------------------|------------------:|--------------------------:|-------------------------:|----------------:|----------------:|--------:|
| avg(LightGBM + conformal, Chronos-2) |            356.78 |                     82.83 |                    89.52 |         4163.23 |            2.25 |     897 |
| official + conformal (benchmark)     |            467.62 |                     75.92 |                    84.95 |         4257.8  |            2.82 |     897 |
