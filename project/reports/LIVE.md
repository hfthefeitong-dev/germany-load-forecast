# Live forecasts

On-time live forecasts with known actuals: 8 days. The pre-registered evaluation
(live/PREREGISTRATION.md) happens after at least 60 days.

## Point forecasts

| model               |   hours |   MAPE % |
|:--------------------|--------:|---------:|
| official            |     192 |     3.88 |
| official+bc         |     192 |     3.6  |
| lgbm                |     192 |     3.4  |
| chronos             |     192 |     3.59 |
| ensemble            |     192 |     3.21 |
| lgbm_morning        |     192 |     2.5  |
| chronos_morning     |     192 |     3.58 |
| ensemble_morning    |     192 |     2.81 |
| chronos_ft          |     192 |     2.91 |
| ensemble_ft         |     192 |     2.97 |
| ensemble_ft_morning |     192 |     2.38 |

## Probabilistic forecasts

| method                               |   mean pinball MW |   coverage 80 % (P10-P90) |   coverage 90 % (P5-P95) |   width 80 % MW |   median MAPE % |   hours |
|:-------------------------------------|------------------:|--------------------------:|-------------------------:|----------------:|----------------:|--------:|
| avg(LightGBM + conformal, Chronos-2) |            433.51 |                     73.44 |                    80.73 |         4296.86 |            2.9  |     192 |
| official + conformal (benchmark)     |            628.79 |                     69.27 |                    74.48 |         4224.1  |            3.58 |     192 |
