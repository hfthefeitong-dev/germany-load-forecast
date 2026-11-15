# Live forecasts

On-time live forecasts with known actuals: 42 days. The pre-registered evaluation
(live/PREREGISTRATION.md) happens after at least 60 days.

## Point forecasts

| model               |   hours |   MAPE % |
|:--------------------|--------:|---------:|
| official            |     997 |     3.52 |
| official+bc         |     997 |     2.86 |
| lgbm                |     997 |     2.5  |
| chronos             |     997 |     2.51 |
| ensemble            |     997 |     2.3  |
| lgbm_morning        |     997 |     2.18 |
| chronos_morning     |     997 |     2.33 |
| ensemble_morning    |     997 |     2.08 |
| chronos_ft          |     997 |     2.31 |
| ensemble_ft         |     997 |     2.25 |
| ensemble_ft_morning |     997 |     2.02 |

## Probabilistic forecasts

| method                               |   mean pinball MW |   coverage 80 % (P10-P90) |   coverage 90 % (P5-P95) |   width 80 % MW |   median MAPE % |   hours |
|:-------------------------------------|------------------:|--------------------------:|-------------------------:|----------------:|----------------:|--------:|
| avg(LightGBM + conformal, Chronos-2) |            352.04 |                     82.65 |                    89.87 |         4108.95 |            2.23 |     997 |
| official + conformal (benchmark)     |            481.34 |                     74.02 |                    83.55 |         4279.12 |            2.88 |     997 |
