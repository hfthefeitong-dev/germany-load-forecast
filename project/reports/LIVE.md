# Live forecasts

On-time live forecasts with known actuals: 29 days. The pre-registered evaluation
(live/PREREGISTRATION.md) happens after at least 60 days.

## Point forecasts

| model               |   hours |   MAPE % |
|:--------------------|--------:|---------:|
| official            |     683 |     3.29 |
| official+bc         |     683 |     2.93 |
| lgbm                |     683 |     2.49 |
| chronos             |     683 |     2.77 |
| ensemble            |     683 |     2.38 |
| lgbm_morning        |     683 |     2.26 |
| chronos_morning     |     683 |     2.59 |
| ensemble_morning    |     683 |     2.23 |
| chronos_ft          |     683 |     2.48 |
| ensemble_ft         |     683 |     2.31 |
| ensemble_ft_morning |     683 |     2.09 |

## Probabilistic forecasts

| method                               |   mean pinball MW |   coverage 80 % (P10-P90) |   coverage 90 % (P5-P95) |   width 80 % MW |   median MAPE % |   hours |
|:-------------------------------------|------------------:|--------------------------:|-------------------------:|----------------:|----------------:|--------:|
| avg(LightGBM + conformal, Chronos-2) |            360.2  |                     84.92 |                    90.63 |         4222.06 |            2.32 |     683 |
| official + conformal (benchmark)     |            482.67 |                     78.04 |                    84.04 |         4234.28 |            2.92 |     683 |
