# Live forecasts

On-time live forecasts with known actuals: 35 days. The pre-registered evaluation
(live/PREREGISTRATION.md) happens after at least 60 days.

## Point forecasts

| model               |   hours |   MAPE % |
|:--------------------|--------:|---------:|
| official            |     827 |     3.46 |
| official+bc         |     827 |     2.8  |
| lgbm                |     827 |     2.52 |
| chronos             |     827 |     2.7  |
| ensemble            |     827 |     2.39 |
| lgbm_morning        |     827 |     2.29 |
| chronos_morning     |     827 |     2.5  |
| ensemble_morning    |     827 |     2.22 |
| chronos_ft          |     827 |     2.38 |
| ensemble_ft         |     827 |     2.28 |
| ensemble_ft_morning |     827 |     2.11 |

## Probabilistic forecasts

| method                               |   mean pinball MW |   coverage 80 % (P10-P90) |   coverage 90 % (P5-P95) |   width 80 % MW |   median MAPE % |   hours |
|:-------------------------------------|------------------:|--------------------------:|-------------------------:|----------------:|----------------:|--------:|
| avg(LightGBM + conformal, Chronos-2) |            362.26 |                     82.22 |                    89.24 |         4188.04 |            2.3  |     827 |
| official + conformal (benchmark)     |            469.14 |                     75.57 |                    84.89 |         4243.6  |            2.88 |     827 |
