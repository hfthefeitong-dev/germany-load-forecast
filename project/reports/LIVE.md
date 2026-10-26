# Live forecasts

On-time live forecasts with known actuals: 22 days. The pre-registered evaluation
(live/PREREGISTRATION.md) happens after at least 60 days.

## Point forecasts

| model               |   hours |   MAPE % |
|:--------------------|--------:|---------:|
| official            |     529 |     3.35 |
| official+bc         |     529 |     3.06 |
| lgbm                |     529 |     2.52 |
| chronos             |     529 |     2.65 |
| ensemble            |     529 |     2.36 |
| lgbm_morning        |     529 |     2.2  |
| chronos_morning     |     529 |     2.61 |
| ensemble_morning    |     529 |     2.23 |
| chronos_ft          |     529 |     2.29 |
| ensemble_ft         |     529 |     2.25 |
| ensemble_ft_morning |     529 |     2.07 |

## Probabilistic forecasts

| method                               |   mean pinball MW |   coverage 80 % (P10-P90) |   coverage 90 % (P5-P95) |   width 80 % MW |   median MAPE % |   hours |
|:-------------------------------------|------------------:|--------------------------:|-------------------------:|----------------:|----------------:|--------:|
| avg(LightGBM + conformal, Chronos-2) |            345.19 |                     83.55 |                    89.79 |         4165.93 |            2.24 |     529 |
| official + conformal (benchmark)     |            507.32 |                     74.86 |                    81.1  |         4222.79 |            3.04 |     529 |
