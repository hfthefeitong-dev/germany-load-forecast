# Live forecasts

On-time live forecasts with known actuals: 20 days. The pre-registered evaluation
(live/PREREGISTRATION.md) happens after at least 60 days.

## Point forecasts

| model               |   hours |   MAPE % |
|:--------------------|--------:|---------:|
| official            |     466 |     3.48 |
| official+bc         |     466 |     3.26 |
| lgbm                |     466 |     2.56 |
| chronos             |     466 |     2.74 |
| ensemble            |     466 |     2.42 |
| lgbm_morning        |     466 |     2.2  |
| chronos_morning     |     466 |     2.71 |
| ensemble_morning    |     466 |     2.31 |
| chronos_ft          |     466 |     2.32 |
| ensemble_ft         |     466 |     2.29 |
| ensemble_ft_morning |     466 |     2.07 |

## Probabilistic forecasts

| method                               |   mean pinball MW |   coverage 80 % (P10-P90) |   coverage 90 % (P5-P95) |   width 80 % MW |   median MAPE % |   hours |
|:-------------------------------------|------------------:|--------------------------:|-------------------------:|----------------:|----------------:|--------:|
| avg(LightGBM + conformal, Chronos-2) |            355.76 |                     82.62 |                    88.84 |         4188.72 |            2.31 |     466 |
| official + conformal (benchmark)     |            532.52 |                     73.39 |                    79.61 |         4183.43 |            3.2  |     466 |
