# Live forecasts

On-time live forecasts with known actuals: 41 days. The pre-registered evaluation
(live/PREREGISTRATION.md) happens after at least 60 days.

## Point forecasts

| model               |   hours |   MAPE % |
|:--------------------|--------:|---------:|
| official            |     971 |     3.57 |
| official+bc         |     971 |     2.81 |
| lgbm                |     971 |     2.49 |
| chronos             |     971 |     2.52 |
| ensemble            |     971 |     2.3  |
| lgbm_morning        |     971 |     2.19 |
| chronos_morning     |     971 |     2.33 |
| ensemble_morning    |     971 |     2.09 |
| chronos_ft          |     971 |     2.26 |
| ensemble_ft         |     971 |     2.22 |
| ensemble_ft_morning |     971 |     2.01 |

## Probabilistic forecasts

| method                               |   mean pinball MW |   coverage 80 % (P10-P90) |   coverage 90 % (P5-P95) |   width 80 % MW |   median MAPE % |   hours |
|:-------------------------------------|------------------:|--------------------------:|-------------------------:|----------------:|----------------:|--------:|
| avg(LightGBM + conformal, Chronos-2) |            350.91 |                     82.9  |                    90.01 |         4120.05 |            2.21 |     971 |
| official + conformal (benchmark)     |            482.55 |                     74.05 |                    83.73 |         4271.15 |            2.88 |     971 |
