# Live forecasts

On-time live forecasts with known actuals: 7 days. The pre-registered evaluation
(live/PREREGISTRATION.md) happens after at least 60 days.

## Point forecasts

| model               |   hours |   MAPE % |
|:--------------------|--------:|---------:|
| official            |     153 |     4.21 |
| official+bc         |     153 |     3.9  |
| lgbm                |     153 |     3.63 |
| chronos             |     153 |     4.04 |
| ensemble            |     153 |     3.49 |
| lgbm_morning        |     153 |     2.61 |
| chronos_morning     |     153 |     4.06 |
| ensemble_morning    |     153 |     3.09 |
| chronos_ft          |     153 |     3.34 |
| ensemble_ft         |     153 |     3.29 |
| ensemble_ft_morning |     153 |     2.59 |

## Probabilistic forecasts

| method                               |   mean pinball MW |   coverage 80 % (P10-P90) |   coverage 90 % (P5-P95) |   width 80 % MW |   median MAPE % |   hours |
|:-------------------------------------|------------------:|--------------------------:|-------------------------:|----------------:|----------------:|--------:|
| avg(LightGBM + conformal, Chronos-2) |            445.79 |                     73.2  |                    77.78 |         4312.46 |            2.94 |     153 |
| official + conformal (benchmark)     |            670.03 |                     66.67 |                    72.55 |         4243.77 |            3.86 |     153 |
