# Live forecasts

On-time live forecasts with known actuals: 47 days. The pre-registered evaluation
(live/PREREGISTRATION.md) happens after at least 60 days.

## Point forecasts

| model               |   hours |   MAPE % |
|:--------------------|--------:|---------:|
| official            |    1129 |     3.35 |
| official+bc         |    1129 |     2.95 |
| lgbm                |    1129 |     2.5  |
| chronos             |    1129 |     2.47 |
| ensemble            |    1129 |     2.28 |
| lgbm_morning        |    1129 |     2.16 |
| chronos_morning     |    1129 |     2.31 |
| ensemble_morning    |    1129 |     2.07 |
| chronos_ft          |    1129 |     2.3  |
| ensemble_ft         |    1129 |     2.22 |
| ensemble_ft_morning |    1129 |     2.02 |

## Probabilistic forecasts

| method                               |   mean pinball MW |   coverage 80 % (P10-P90) |   coverage 90 % (P5-P95) |   width 80 % MW |   median MAPE % |   hours |
|:-------------------------------------|------------------:|--------------------------:|-------------------------:|----------------:|----------------:|--------:|
| avg(LightGBM + conformal, Chronos-2) |            357.15 |                     82.11 |                    89.37 |         4113.75 |            2.24 |    1129 |
| official + conformal (benchmark)     |            479.6  |                     73.6  |                    83.35 |         4306.07 |            2.89 |    1129 |
