# Live forecasts

On-time live forecasts with known actuals: 32 days. The pre-registered evaluation
(live/PREREGISTRATION.md) happens after at least 60 days.

## Point forecasts

| model               |   hours |   MAPE % |
|:--------------------|--------:|---------:|
| official            |     755 |     3.36 |
| official+bc         |     755 |     2.82 |
| lgbm                |     755 |     2.42 |
| chronos             |     755 |     2.71 |
| ensemble            |     755 |     2.33 |
| lgbm_morning        |     755 |     2.2  |
| chronos_morning     |     755 |     2.53 |
| ensemble_morning    |     755 |     2.19 |
| chronos_ft          |     755 |     2.41 |
| ensemble_ft         |     755 |     2.24 |
| ensemble_ft_morning |     755 |     2.07 |

## Probabilistic forecasts

| method                               |   mean pinball MW |   coverage 80 % (P10-P90) |   coverage 90 % (P5-P95) |   width 80 % MW |   median MAPE % |   hours |
|:-------------------------------------|------------------:|--------------------------:|-------------------------:|----------------:|----------------:|--------:|
| avg(LightGBM + conformal, Chronos-2) |            355.29 |                     83.58 |                    89.93 |         4205.88 |            2.25 |     755 |
| official + conformal (benchmark)     |            474.37 |                     76.42 |                    84.37 |         4232.05 |            2.88 |     755 |
