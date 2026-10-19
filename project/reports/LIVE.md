# Live forecasts

On-time live forecasts with known actuals: 16 days. The pre-registered evaluation
(live/PREREGISTRATION.md) happens after at least 60 days.

## Point forecasts

| model               |   hours |   MAPE % |
|:--------------------|--------:|---------:|
| official            |     371 |     3.35 |
| official+bc         |     371 |     3.28 |
| lgbm                |     371 |     2.76 |
| chronos             |     371 |     2.9  |
| ensemble            |     371 |     2.6  |
| lgbm_morning        |     371 |     2.29 |
| chronos_morning     |     371 |     2.9  |
| ensemble_morning    |     371 |     2.43 |
| chronos_ft          |     371 |     2.38 |
| ensemble_ft         |     371 |     2.42 |
| ensemble_ft_morning |     371 |     2.13 |

## Probabilistic forecasts

| method                               |   mean pinball MW |   coverage 80 % (P10-P90) |   coverage 90 % (P5-P95) |   width 80 % MW |   median MAPE % |   hours |
|:-------------------------------------|------------------:|--------------------------:|-------------------------:|----------------:|----------------:|--------:|
| avg(LightGBM + conformal, Chronos-2) |            363.88 |                     81.67 |                    88.95 |         4222.07 |            2.45 |     371 |
| official + conformal (benchmark)     |            517.95 |                     75.47 |                    80.05 |         4180.32 |            3.18 |     371 |
