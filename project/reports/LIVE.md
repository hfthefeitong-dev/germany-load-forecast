# Live forecasts

On-time live forecasts with known actuals: 18 days. The pre-registered evaluation
(live/PREREGISTRATION.md) happens after at least 60 days.

## Point forecasts

| model               |   hours |   MAPE % |
|:--------------------|--------:|---------:|
| official            |     418 |     3.26 |
| official+bc         |     418 |     3.13 |
| lgbm                |     418 |     2.64 |
| chronos             |     418 |     2.77 |
| ensemble            |     418 |     2.47 |
| lgbm_morning        |     418 |     2.18 |
| chronos_morning     |     418 |     2.76 |
| ensemble_morning    |     418 |     2.31 |
| chronos_ft          |     418 |     2.3  |
| ensemble_ft         |     418 |     2.3  |
| ensemble_ft_morning |     418 |     2.04 |

## Probabilistic forecasts

| method                               |   mean pinball MW |   coverage 80 % (P10-P90) |   coverage 90 % (P5-P95) |   width 80 % MW |   median MAPE % |   hours |
|:-------------------------------------|------------------:|--------------------------:|-------------------------:|----------------:|----------------:|--------:|
| avg(LightGBM + conformal, Chronos-2) |            352.06 |                     83.01 |                    89.95 |         4204.2  |            2.35 |     418 |
| official + conformal (benchmark)     |            498.99 |                     76.56 |                    81.58 |         4183.66 |            3.06 |     418 |
