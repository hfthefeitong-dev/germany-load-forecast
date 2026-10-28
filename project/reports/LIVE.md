# Live forecasts

On-time live forecasts with known actuals: 24 days. The pre-registered evaluation
(live/PREREGISTRATION.md) happens after at least 60 days.

## Point forecasts

| model               |   hours |   MAPE % |
|:--------------------|--------:|---------:|
| official            |     563 |     3.35 |
| official+bc         |     563 |     2.98 |
| lgbm                |     563 |     2.49 |
| chronos             |     563 |     2.75 |
| ensemble            |     563 |     2.4  |
| lgbm_morning        |     563 |     2.17 |
| chronos_morning     |     563 |     2.6  |
| ensemble_morning    |     563 |     2.21 |
| chronos_ft          |     563 |     2.4  |
| ensemble_ft         |     563 |     2.29 |
| ensemble_ft_morning |     563 |     2.04 |

## Probabilistic forecasts

| method                               |   mean pinball MW |   coverage 80 % (P10-P90) |   coverage 90 % (P5-P95) |   width 80 % MW |   median MAPE % |   hours |
|:-------------------------------------|------------------:|--------------------------:|-------------------------:|----------------:|----------------:|--------:|
| avg(LightGBM + conformal, Chronos-2) |            351.66 |                     83.3  |                    89.7  |         4163.61 |            2.31 |     563 |
| official + conformal (benchmark)     |            496.36 |                     75.67 |                    82.06 |         4213.76 |            2.98 |     563 |
