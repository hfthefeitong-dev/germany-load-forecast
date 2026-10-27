# Live forecasts

On-time live forecasts with known actuals: 23 days. The pre-registered evaluation
(live/PREREGISTRATION.md) happens after at least 60 days.

## Point forecasts

| model               |   hours |   MAPE % |
|:--------------------|--------:|---------:|
| official            |     539 |     3.34 |
| official+bc         |     539 |     3.01 |
| lgbm                |     539 |     2.49 |
| chronos             |     539 |     2.74 |
| ensemble            |     539 |     2.39 |
| lgbm_morning        |     539 |     2.16 |
| chronos_morning     |     539 |     2.65 |
| ensemble_morning    |     539 |     2.23 |
| chronos_ft          |     539 |     2.37 |
| ensemble_ft         |     539 |     2.28 |
| ensemble_ft_morning |     539 |     2.06 |

## Probabilistic forecasts

| method                               |   mean pinball MW |   coverage 80 % (P10-P90) |   coverage 90 % (P5-P95) |   width 80 % MW |   median MAPE % |   hours |
|:-------------------------------------|------------------:|--------------------------:|-------------------------:|----------------:|----------------:|--------:|
| avg(LightGBM + conformal, Chronos-2) |            350.54 |                     82.93 |                    89.42 |         4162.35 |            2.28 |     539 |
| official + conformal (benchmark)     |            501.09 |                     75.7  |                    81.82 |         4209.92 |            2.99 |     539 |
