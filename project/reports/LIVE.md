# Live forecasts

On-time live forecasts with known actuals: 48 days. The pre-registered evaluation
(live/PREREGISTRATION.md) happens after at least 60 days.

## Point forecasts

| model               |   hours |   MAPE % |
|:--------------------|--------:|---------:|
| official            |    1140 |     3.36 |
| official+bc         |    1140 |     2.94 |
| lgbm                |    1140 |     2.49 |
| chronos             |    1140 |     2.47 |
| ensemble            |    1140 |     2.27 |
| lgbm_morning        |    1140 |     2.16 |
| chronos_morning     |    1140 |     2.32 |
| ensemble_morning    |    1140 |     2.08 |
| chronos_ft          |    1140 |     2.3  |
| ensemble_ft         |    1140 |     2.22 |
| ensemble_ft_morning |    1140 |     2.02 |

## Probabilistic forecasts

| method                               |   mean pinball MW |   coverage 80 % (P10-P90) |   coverage 90 % (P5-P95) |   width 80 % MW |   median MAPE % |   hours |
|:-------------------------------------|------------------:|--------------------------:|-------------------------:|----------------:|----------------:|--------:|
| avg(LightGBM + conformal, Chronos-2) |            356.44 |                     82.19 |                    89.3  |         4109.13 |            2.23 |    1140 |
| official + conformal (benchmark)     |            478.03 |                     73.6  |                    83.33 |         4300.09 |            2.88 |    1140 |
