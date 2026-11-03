# Live forecasts

On-time live forecasts with known actuals: 30 days. The pre-registered evaluation
(live/PREREGISTRATION.md) happens after at least 60 days.

## Point forecasts

| model               |   hours |   MAPE % |
|:--------------------|--------:|---------:|
| official            |     708 |     3.19 |
| official+bc         |     708 |     2.81 |
| lgbm                |     708 |     2.42 |
| chronos             |     708 |     2.67 |
| ensemble            |     708 |     2.3  |
| lgbm_morning        |     708 |     2.22 |
| chronos_morning     |     708 |     2.51 |
| ensemble_morning    |     708 |     2.19 |
| chronos_ft          |     708 |     2.39 |
| ensemble_ft         |     708 |     2.23 |
| ensemble_ft_morning |     708 |     2.06 |

## Probabilistic forecasts

| method                               |   mean pinball MW |   coverage 80 % (P10-P90) |   coverage 90 % (P5-P95) |   width 80 % MW |   median MAPE % |   hours |
|:-------------------------------------|------------------:|--------------------------:|-------------------------:|----------------:|----------------:|--------:|
| avg(LightGBM + conformal, Chronos-2) |            349.29 |                     84.75 |                    90.68 |         4217.06 |            2.24 |     708 |
| official + conformal (benchmark)     |            464.06 |                     78.53 |                    84.75 |         4234.62 |            2.8  |     708 |
