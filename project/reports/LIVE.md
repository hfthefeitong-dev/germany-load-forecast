# Live forecasts

On-time live forecasts with known actuals: 21 days. The pre-registered evaluation
(live/PREREGISTRATION.md) happens after at least 60 days.

## Point forecasts

| model               |   hours |   MAPE % |
|:--------------------|--------:|---------:|
| official            |     490 |     3.45 |
| official+bc         |     490 |     3.19 |
| lgbm                |     490 |     2.52 |
| chronos             |     490 |     2.69 |
| ensemble            |     490 |     2.38 |
| lgbm_morning        |     490 |     2.2  |
| chronos_morning     |     490 |     2.66 |
| ensemble_morning    |     490 |     2.28 |
| chronos_ft          |     490 |     2.28 |
| ensemble_ft         |     490 |     2.25 |
| ensemble_ft_morning |     490 |     2.07 |

## Probabilistic forecasts

| method                               |   mean pinball MW |   coverage 80 % (P10-P90) |   coverage 90 % (P5-P95) |   width 80 % MW |   median MAPE % |   hours |
|:-------------------------------------|------------------:|--------------------------:|-------------------------:|----------------:|----------------:|--------:|
| avg(LightGBM + conformal, Chronos-2) |            351.66 |                     83.27 |                    89.39 |         4187.96 |            2.28 |     490 |
| official + conformal (benchmark)     |            526.64 |                     73.47 |                    80    |         4195.81 |            3.16 |     490 |
