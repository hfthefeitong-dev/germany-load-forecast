# Live forecasts

On-time live forecasts with known actuals: 5 days. The pre-registered evaluation
(live/PREREGISTRATION.md) happens after at least 60 days.

## Point forecasts

| model               |   hours |   MAPE % |
|:--------------------|--------:|---------:|
| official            |     106 |     5.22 |
| official+bc         |     106 |     4.89 |
| lgbm                |     106 |     4.09 |
| chronos             |     106 |     5.14 |
| ensemble            |     106 |     4.46 |
| lgbm_morning        |     106 |     3.03 |
| chronos_morning     |     106 |     5.19 |
| ensemble_morning    |     106 |     3.96 |
| chronos_ft          |     106 |     4.22 |
| ensemble_ft         |     106 |     4.07 |
| ensemble_ft_morning |     106 |     3.21 |

## Probabilistic forecasts

| method                               |   mean pinball MW |   coverage 80 % (P10-P90) |   coverage 90 % (P5-P95) |   width 80 % MW |   median MAPE % |   hours |
|:-------------------------------------|------------------:|--------------------------:|-------------------------:|----------------:|----------------:|--------:|
| avg(LightGBM + conformal, Chronos-2) |            542.25 |                     61.32 |                    68.87 |         4445.98 |            3.7  |     106 |
| official + conformal (benchmark)     |            846.96 |                     52.83 |                    60.38 |         4277.26 |            4.77 |     106 |
