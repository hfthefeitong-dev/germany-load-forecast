# Live forecasts

On-time live forecasts with known actuals: 25 days. The pre-registered evaluation
(live/PREREGISTRATION.md) happens after at least 60 days.

## Point forecasts

| model               |   hours |   MAPE % |
|:--------------------|--------:|---------:|
| official            |     587 |     3.32 |
| official+bc         |     587 |     2.93 |
| lgbm                |     587 |     2.48 |
| chronos             |     587 |     2.71 |
| ensemble            |     587 |     2.37 |
| lgbm_morning        |     587 |     2.16 |
| chronos_morning     |     587 |     2.57 |
| ensemble_morning    |     587 |     2.19 |
| chronos_ft          |     587 |     2.38 |
| ensemble_ft         |     587 |     2.27 |
| ensemble_ft_morning |     587 |     2.03 |

## Probabilistic forecasts

| method                               |   mean pinball MW |   coverage 80 % (P10-P90) |   coverage 90 % (P5-P95) |   width 80 % MW |   median MAPE % |   hours |
|:-------------------------------------|------------------:|--------------------------:|-------------------------:|----------------:|----------------:|--------:|
| avg(LightGBM + conformal, Chronos-2) |            348.63 |                     83.82 |                    89.95 |         4171.84 |            2.28 |     587 |
| official + conformal (benchmark)     |            489.19 |                     76.49 |                    82.79 |         4219.45 |            2.95 |     587 |
