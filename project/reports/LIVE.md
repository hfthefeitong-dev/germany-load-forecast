# Live forecasts

On-time live forecasts with known actuals: 2 days. The pre-registered evaluation
(live/PREREGISTRATION.md) happens after at least 60 days.

## Point forecasts

| model               |   hours |   MAPE % |
|:--------------------|--------:|---------:|
| official            |      34 |     9.2  |
| official+bc         |      34 |     8.78 |
| lgbm                |      34 |     4.69 |
| chronos             |      34 |     6.02 |
| ensemble            |      34 |     5.33 |
| lgbm_morning        |      34 |     4.17 |
| chronos_morning     |      34 |     7.04 |
| ensemble_morning    |      34 |     5.6  |
| chronos_ft          |      34 |     6.84 |
| ensemble_ft         |      34 |     5.76 |
| ensemble_ft_morning |      34 |     5.2  |

## Probabilistic forecasts

| method                               |   mean pinball MW |   coverage 80 % (P10-P90) |   coverage 90 % (P5-P95) |   width 80 % MW |   median MAPE % |   hours |
|:-------------------------------------|------------------:|--------------------------:|-------------------------:|----------------:|----------------:|--------:|
| avg(LightGBM + conformal, Chronos-2) |            672.71 |                     35.29 |                    47.06 |         4145.92 |            4.5  |      34 |
| official + conformal (benchmark)     |           1660.59 |                      0    |                     2.94 |         4137.37 |            8.73 |      34 |
