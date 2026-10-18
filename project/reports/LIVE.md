# Live forecasts

On-time live forecasts with known actuals: 15 days. The pre-registered evaluation
(live/PREREGISTRATION.md) happens after at least 60 days.

## Point forecasts

| model               |   hours |   MAPE % |
|:--------------------|--------:|---------:|
| official            |     347 |     3.43 |
| official+bc         |     347 |     3.37 |
| lgbm                |     347 |     2.79 |
| chronos             |     347 |     3    |
| ensemble            |     347 |     2.66 |
| lgbm_morning        |     347 |     2.28 |
| chronos_morning     |     347 |     2.91 |
| ensemble_morning    |     347 |     2.42 |
| chronos_ft          |     347 |     2.45 |
| ensemble_ft         |     347 |     2.47 |
| ensemble_ft_morning |     347 |     2.13 |

## Probabilistic forecasts

| method                               |   mean pinball MW |   coverage 80 % (P10-P90) |   coverage 90 % (P5-P95) |   width 80 % MW |   median MAPE % |   hours |
|:-------------------------------------|------------------:|--------------------------:|-------------------------:|----------------:|----------------:|--------:|
| avg(LightGBM + conformal, Chronos-2) |            369.67 |                     80.69 |                    88.18 |         4226.46 |            2.47 |     347 |
| official + conformal (benchmark)     |            530.67 |                     74.93 |                    79.54 |         4179.83 |            3.23 |     347 |
