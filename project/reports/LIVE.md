# Live forecasts

On-time live forecasts with known actuals: 44 days. The pre-registered evaluation
(live/PREREGISTRATION.md) happens after at least 60 days.

## Point forecasts

| model               |   hours |   MAPE % |
|:--------------------|--------:|---------:|
| official            |    1042 |     3.5  |
| official+bc         |    1042 |     2.9  |
| lgbm                |    1042 |     2.52 |
| chronos             |    1042 |     2.54 |
| ensemble            |    1042 |     2.33 |
| lgbm_morning        |    1042 |     2.21 |
| chronos_morning     |    1042 |     2.37 |
| ensemble_morning    |    1042 |     2.12 |
| chronos_ft          |    1042 |     2.35 |
| ensemble_ft         |    1042 |     2.28 |
| ensemble_ft_morning |    1042 |     2.07 |

## Probabilistic forecasts

| method                               |   mean pinball MW |   coverage 80 % (P10-P90) |   coverage 90 % (P5-P95) |   width 80 % MW |   median MAPE % |   hours |
|:-------------------------------------|------------------:|--------------------------:|-------------------------:|----------------:|----------------:|--------:|
| avg(LightGBM + conformal, Chronos-2) |            360.56 |                     82.05 |                    89.25 |         4115.86 |            2.26 |    1042 |
| official + conformal (benchmark)     |            481.43 |                     73.99 |                    83.97 |         4286.87 |            2.9  |    1042 |
