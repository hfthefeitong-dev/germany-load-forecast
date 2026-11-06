# Live forecasts

On-time live forecasts with known actuals: 33 days. The pre-registered evaluation
(live/PREREGISTRATION.md) happens after at least 60 days.

## Point forecasts

| model               |   hours |   MAPE % |
|:--------------------|--------:|---------:|
| official            |     779 |     3.47 |
| official+bc         |     779 |     2.95 |
| lgbm                |     779 |     2.55 |
| chronos             |     779 |     2.83 |
| ensemble            |     779 |     2.46 |
| lgbm_morning        |     779 |     2.33 |
| chronos_morning     |     779 |     2.65 |
| ensemble_morning    |     779 |     2.32 |
| chronos_ft          |     779 |     2.55 |
| ensemble_ft         |     779 |     2.38 |
| ensemble_ft_morning |     779 |     2.2  |

## Probabilistic forecasts

| method                               |   mean pinball MW |   coverage 80 % (P10-P90) |   coverage 90 % (P5-P95) |   width 80 % MW |   median MAPE % |   hours |
|:-------------------------------------|------------------:|--------------------------:|-------------------------:|----------------:|----------------:|--------:|
| avg(LightGBM + conformal, Chronos-2) |            388.62 |                     82.54 |                    88.96 |         4193.15 |            2.39 |     779 |
| official + conformal (benchmark)     |            501.48 |                     75.22 |                    83.44 |         4232.63 |            2.99 |     779 |
