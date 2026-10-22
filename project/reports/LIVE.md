# Live forecasts

On-time live forecasts with known actuals: 19 days. The pre-registered evaluation
(live/PREREGISTRATION.md) happens after at least 60 days.

## Point forecasts

| model               |   hours |   MAPE % |
|:--------------------|--------:|---------:|
| official            |     442 |     3.47 |
| official+bc         |     442 |     3.31 |
| lgbm                |     442 |     2.66 |
| chronos             |     442 |     2.83 |
| ensemble            |     442 |     2.52 |
| lgbm_morning        |     442 |     2.27 |
| chronos_morning     |     442 |     2.82 |
| ensemble_morning    |     442 |     2.39 |
| chronos_ft          |     442 |     2.4  |
| ensemble_ft         |     442 |     2.37 |
| ensemble_ft_morning |     442 |     2.14 |

## Probabilistic forecasts

| method                               |   mean pinball MW |   coverage 80 % (P10-P90) |   coverage 90 % (P5-P95) |   width 80 % MW |   median MAPE % |   hours |
|:-------------------------------------|------------------:|--------------------------:|-------------------------:|----------------:|----------------:|--------:|
| avg(LightGBM + conformal, Chronos-2) |            367.09 |                     81    |                    87.56 |         4193.03 |            2.39 |     442 |
| official + conformal (benchmark)     |            541.09 |                     73.76 |                    79.19 |         4184.41 |            3.24 |     442 |
