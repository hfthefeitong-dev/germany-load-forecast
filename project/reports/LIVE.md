# Live forecasts

On-time live forecasts with known actuals: 31 days. The pre-registered evaluation
(live/PREREGISTRATION.md) happens after at least 60 days.

## Point forecasts

| model               |   hours |   MAPE % |
|:--------------------|--------:|---------:|
| official            |     731 |     3.25 |
| official+bc         |     731 |     2.79 |
| lgbm                |     731 |     2.44 |
| chronos             |     731 |     2.69 |
| ensemble            |     731 |     2.33 |
| lgbm_morning        |     731 |     2.24 |
| chronos_morning     |     731 |     2.55 |
| ensemble_morning    |     731 |     2.22 |
| chronos_ft          |     731 |     2.42 |
| ensemble_ft         |     731 |     2.25 |
| ensemble_ft_morning |     731 |     2.08 |

## Probabilistic forecasts

| method                               |   mean pinball MW |   coverage 80 % (P10-P90) |   coverage 90 % (P5-P95) |   width 80 % MW |   median MAPE % |   hours |
|:-------------------------------------|------------------:|--------------------------:|-------------------------:|----------------:|----------------:|--------:|
| avg(LightGBM + conformal, Chronos-2) |            355.04 |                     83.99 |                    90.01 |         4212.41 |            2.26 |     731 |
| official + conformal (benchmark)     |            464.57 |                     77.98 |                    84.82 |         4232.81 |            2.81 |     731 |
