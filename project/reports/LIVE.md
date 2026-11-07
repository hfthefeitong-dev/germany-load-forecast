# Live forecasts

On-time live forecasts with known actuals: 34 days. The pre-registered evaluation
(live/PREREGISTRATION.md) happens after at least 60 days.

## Point forecasts

| model               |   hours |   MAPE % |
|:--------------------|--------:|---------:|
| official            |     803 |     3.43 |
| official+bc         |     803 |     2.86 |
| lgbm                |     803 |     2.53 |
| chronos             |     803 |     2.77 |
| ensemble            |     803 |     2.42 |
| lgbm_morning        |     803 |     2.32 |
| chronos_morning     |     803 |     2.59 |
| ensemble_morning    |     803 |     2.29 |
| chronos_ft          |     803 |     2.48 |
| ensemble_ft         |     803 |     2.34 |
| ensemble_ft_morning |     803 |     2.17 |

## Probabilistic forecasts

| method                               |   mean pinball MW |   coverage 80 % (P10-P90) |   coverage 90 % (P5-P95) |   width 80 % MW |   median MAPE % |   hours |
|:-------------------------------------|------------------:|--------------------------:|-------------------------:|----------------:|----------------:|--------:|
| avg(LightGBM + conformal, Chronos-2) |            376.74 |                     82.32 |                    88.79 |         4186.32 |            2.35 |     803 |
| official + conformal (benchmark)     |            482.88 |                     74.97 |                    83.81 |         4237.35 |            2.91 |     803 |
