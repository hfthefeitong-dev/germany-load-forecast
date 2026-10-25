# Live forecasts

On-time live forecasts with known actuals: 22 days. The pre-registered evaluation
(live/PREREGISTRATION.md) happens after at least 60 days.

## Point forecasts

| model               |   hours |   MAPE % |
|:--------------------|--------:|---------:|
| official            |     515 |     3.4  |
| official+bc         |     515 |     3.09 |
| lgbm                |     515 |     2.57 |
| chronos             |     515 |     2.68 |
| ensemble            |     515 |     2.4  |
| lgbm_morning        |     515 |     2.24 |
| chronos_morning     |     515 |     2.64 |
| ensemble_morning    |     515 |     2.28 |
| chronos_ft          |     515 |     2.3  |
| ensemble_ft         |     515 |     2.28 |
| ensemble_ft_morning |     515 |     2.11 |

## Probabilistic forecasts

| method                               |   mean pinball MW |   coverage 80 % (P10-P90) |   coverage 90 % (P5-P95) |   width 80 % MW |   median MAPE % |   hours |
|:-------------------------------------|------------------:|--------------------------:|-------------------------:|----------------:|----------------:|--------:|
| avg(LightGBM + conformal, Chronos-2) |            350.03 |                     82.91 |                    89.32 |         4171.35 |            2.29 |     515 |
| official + conformal (benchmark)     |            512.86 |                     74.56 |                    80.97 |         4204.55 |            3.08 |     515 |
