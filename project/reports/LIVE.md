# Live forecasts

On-time live forecasts with known actuals: 12 days. The pre-registered evaluation
(live/PREREGISTRATION.md) happens after at least 60 days.

## Point forecasts

| model               |   hours |   MAPE % |
|:--------------------|--------:|---------:|
| official            |     275 |     3.73 |
| official+bc         |     275 |     3.76 |
| lgbm                |     275 |     3.12 |
| chronos             |     275 |     3.33 |
| ensemble            |     275 |     2.98 |
| lgbm_morning        |     275 |     2.46 |
| chronos_morning     |     275 |     3.29 |
| ensemble_morning    |     275 |     2.69 |
| chronos_ft          |     275 |     2.69 |
| ensemble_ft         |     275 |     2.74 |
| ensemble_ft_morning |     275 |     2.32 |

## Probabilistic forecasts

| method                               |   mean pinball MW |   coverage 80 % (P10-P90) |   coverage 90 % (P5-P95) |   width 80 % MW |   median MAPE % |   hours |
|:-------------------------------------|------------------:|--------------------------:|-------------------------:|----------------:|----------------:|--------:|
| avg(LightGBM + conformal, Chronos-2) |            402.09 |                     76.73 |                    84.73 |         4264.23 |            2.7  |     275 |
| official + conformal (benchmark)     |            598.22 |                     69.45 |                    74.18 |         4196.34 |            3.57 |     275 |
