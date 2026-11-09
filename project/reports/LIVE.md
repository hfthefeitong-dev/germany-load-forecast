# Live forecasts

On-time live forecasts with known actuals: 36 days. The pre-registered evaluation
(live/PREREGISTRATION.md) happens after at least 60 days.

## Point forecasts

| model               |   hours |   MAPE % |
|:--------------------|--------:|---------:|
| official            |     851 |     3.46 |
| official+bc         |     851 |     2.8  |
| lgbm                |     851 |     2.52 |
| chronos             |     851 |     2.7  |
| ensemble            |     851 |     2.39 |
| lgbm_morning        |     851 |     2.3  |
| chronos_morning     |     851 |     2.49 |
| ensemble_morning    |     851 |     2.23 |
| chronos_ft          |     851 |     2.38 |
| ensemble_ft         |     851 |     2.29 |
| ensemble_ft_morning |     851 |     2.13 |

## Probabilistic forecasts

| method                               |   mean pinball MW |   coverage 80 % (P10-P90) |   coverage 90 % (P5-P95) |   width 80 % MW |   median MAPE % |   hours |
|:-------------------------------------|------------------:|--------------------------:|-------------------------:|----------------:|----------------:|--------:|
| avg(LightGBM + conformal, Chronos-2) |            362.55 |                     82.02 |                    88.95 |         4183.9  |            2.31 |     851 |
| official + conformal (benchmark)     |            469.79 |                     75.56 |                    84.72 |         4250.13 |            2.88 |     851 |
