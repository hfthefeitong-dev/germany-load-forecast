# Live forecasts

On-time live forecasts with known actuals: 42 days. The pre-registered evaluation
(live/PREREGISTRATION.md) happens after at least 60 days.

## Point forecasts

| model               |   hours |   MAPE % |
|:--------------------|--------:|---------:|
| official            |    1009 |     3.57 |
| official+bc         |    1009 |     2.99 |
| lgbm                |    1009 |     2.6  |
| chronos             |    1009 |     2.6  |
| ensemble            |    1009 |     2.4  |
| lgbm_morning        |    1009 |     2.27 |
| chronos_morning     |    1009 |     2.42 |
| ensemble_morning    |    1009 |     2.17 |
| chronos_ft          |    1009 |     2.43 |
| ensemble_ft         |    1009 |     2.36 |
| ensemble_ft_morning |    1009 |     2.12 |

## Probabilistic forecasts

| method                               |   mean pinball MW |   coverage 80 % (P10-P90) |   coverage 90 % (P5-P95) |   width 80 % MW |   median MAPE % |   hours |
|:-------------------------------------|------------------:|--------------------------:|-------------------------:|----------------:|----------------:|--------:|
| avg(LightGBM + conformal, Chronos-2) |            373.71 |                     81.47 |                    88.7  |         4108.71 |            2.34 |    1009 |
| official + conformal (benchmark)     |            498.35 |                     73.34 |                    82.85 |         4291.15 |            2.98 |    1009 |
