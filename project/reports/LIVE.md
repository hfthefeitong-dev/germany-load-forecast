# Live forecasts

On-time live forecasts with known actuals: 17 days. The pre-registered evaluation
(live/PREREGISTRATION.md) happens after at least 60 days.

## Point forecasts

| model               |   hours |   MAPE % |
|:--------------------|--------:|---------:|
| official            |     394 |     3.26 |
| official+bc         |     394 |     3.19 |
| lgbm                |     394 |     2.7  |
| chronos             |     394 |     2.81 |
| ensemble            |     394 |     2.51 |
| lgbm_morning        |     394 |     2.22 |
| chronos_morning     |     394 |     2.8  |
| ensemble_morning    |     394 |     2.35 |
| chronos_ft          |     394 |     2.32 |
| ensemble_ft         |     394 |     2.35 |
| ensemble_ft_morning |     394 |     2.06 |

## Probabilistic forecasts

| method                               |   mean pinball MW |   coverage 80 % (P10-P90) |   coverage 90 % (P5-P95) |   width 80 % MW |   median MAPE % |   hours |
|:-------------------------------------|------------------:|--------------------------:|-------------------------:|----------------:|----------------:|--------:|
| avg(LightGBM + conformal, Chronos-2) |            356.69 |                     82.23 |                    89.59 |          4214.3 |            2.38 |     394 |
| official + conformal (benchmark)     |            506.55 |                     76.14 |                    81.47 |          4184.3 |            3.11 |     394 |
