# Live forecasts

On-time live forecasts with known actuals: 26 days. The pre-registered evaluation
(live/PREREGISTRATION.md) happens after at least 60 days.

## Point forecasts

| model               |   hours |   MAPE % |
|:--------------------|--------:|---------:|
| official            |     611 |     3.32 |
| official+bc         |     611 |     2.88 |
| lgbm                |     611 |     2.45 |
| chronos             |     611 |     2.69 |
| ensemble            |     611 |     2.34 |
| lgbm_morning        |     611 |     2.14 |
| chronos_morning     |     611 |     2.54 |
| ensemble_morning    |     611 |     2.17 |
| chronos_ft          |     611 |     2.38 |
| ensemble_ft         |     611 |     2.26 |
| ensemble_ft_morning |     611 |     2.01 |

## Probabilistic forecasts

| method                               |   mean pinball MW |   coverage 80 % (P10-P90) |   coverage 90 % (P5-P95) |   width 80 % MW |   median MAPE % |   hours |
|:-------------------------------------|------------------:|--------------------------:|-------------------------:|----------------:|----------------:|--------:|
| avg(LightGBM + conformal, Chronos-2) |            349.33 |                     84.29 |                    90.18 |         4173.84 |            2.26 |     611 |
| official + conformal (benchmark)     |            486.27 |                     77.25 |                    83.31 |         4225    |            2.92 |     611 |
