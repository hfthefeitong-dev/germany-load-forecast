# Live forecasts

On-time live forecasts with known actuals: 43 days. The pre-registered evaluation
(live/PREREGISTRATION.md) happens after at least 60 days.

## Point forecasts

| model               |   hours |   MAPE % |
|:--------------------|--------:|---------:|
| official            |    1019 |     3.5  |
| official+bc         |    1019 |     2.91 |
| lgbm                |    1019 |     2.51 |
| chronos             |    1019 |     2.53 |
| ensemble            |    1019 |     2.32 |
| lgbm_morning        |    1019 |     2.2  |
| chronos_morning     |    1019 |     2.35 |
| ensemble_morning    |    1019 |     2.1  |
| chronos_ft          |    1019 |     2.34 |
| ensemble_ft         |    1019 |     2.28 |
| ensemble_ft_morning |    1019 |     2.05 |

## Probabilistic forecasts

| method                               |   mean pinball MW |   coverage 80 % (P10-P90) |   coverage 90 % (P5-P95) |   width 80 % MW |   median MAPE % |   hours |
|:-------------------------------------|------------------:|--------------------------:|-------------------------:|----------------:|----------------:|--------:|
| avg(LightGBM + conformal, Chronos-2) |            356.98 |                     82.04 |                    89.21 |         4108.19 |            2.26 |    1019 |
| official + conformal (benchmark)     |            481.65 |                     73.9  |                    83.61 |         4282.28 |            2.9  |    1019 |
