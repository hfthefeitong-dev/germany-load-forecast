# Live forecasts

On-time live forecasts with known actuals: 3 days. The pre-registered evaluation
(live/PREREGISTRATION.md) happens after at least 60 days.

## Point forecasts

| model               |   hours |   MAPE % |
|:--------------------|--------:|---------:|
| official            |      58 |     7.41 |
| official+bc         |      58 |     6.97 |
| lgbm                |      58 |     4.41 |
| chronos             |      58 |     7.41 |
| ensemble            |      58 |     5.86 |
| lgbm_morning        |      58 |     3.51 |
| chronos_morning     |      58 |     7.84 |
| ensemble_morning    |      58 |     5.54 |
| chronos_ft          |      58 |     5.78 |
| ensemble_ft         |      58 |     5.07 |
| ensemble_ft_morning |      58 |     4.12 |

## Probabilistic forecasts

| method                               |   mean pinball MW |   coverage 80 % (P10-P90) |   coverage 90 % (P5-P95) |   width 80 % MW |   median MAPE % |   hours |
|:-------------------------------------|------------------:|--------------------------:|-------------------------:|----------------:|----------------:|--------:|
| avg(LightGBM + conformal, Chronos-2) |            729.56 |                     39.66 |                    50    |         4582.16 |            4.98 |      58 |
| official + conformal (benchmark)     |           1291.11 |                     20.69 |                    27.59 |         4191.2  |            6.95 |      58 |
