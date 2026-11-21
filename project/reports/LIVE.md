# Live forecasts

On-time live forecasts with known actuals: 47 days. The pre-registered evaluation
(live/PREREGISTRATION.md) happens after at least 60 days.

## Point forecasts

| model               |   hours |   MAPE % |
|:--------------------|--------:|---------:|
| official            |    1116 |     3.38 |
| official+bc         |    1116 |     2.95 |
| lgbm                |    1116 |     2.48 |
| chronos             |    1116 |     2.48 |
| ensemble            |    1116 |     2.27 |
| lgbm_morning        |    1116 |     2.16 |
| chronos_morning     |    1116 |     2.31 |
| ensemble_morning    |    1116 |     2.07 |
| chronos_ft          |    1116 |     2.3  |
| ensemble_ft         |    1116 |     2.21 |
| ensemble_ft_morning |    1116 |     2.02 |

## Probabilistic forecasts

| method                               |   mean pinball MW |   coverage 80 % (P10-P90) |   coverage 90 % (P5-P95) |   width 80 % MW |   median MAPE % |   hours |
|:-------------------------------------|------------------:|--------------------------:|-------------------------:|----------------:|----------------:|--------:|
| avg(LightGBM + conformal, Chronos-2) |            355.7  |                     82.35 |                    89.43 |         4111.19 |            2.22 |    1116 |
| official + conformal (benchmark)     |            479.99 |                     73.48 |                    83.33 |         4295.07 |            2.89 |    1116 |
