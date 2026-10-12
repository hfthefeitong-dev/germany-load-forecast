# Live forecasts

On-time live forecasts with known actuals: 10 days. The pre-registered evaluation
(live/PREREGISTRATION.md) happens after at least 60 days.

## Point forecasts

| model               |   hours |   MAPE % |
|:--------------------|--------:|---------:|
| official            |     226 |     4.07 |
| official+bc         |     226 |     4.1  |
| lgbm                |     226 |     3.36 |
| chronos             |     226 |     3.61 |
| ensemble            |     226 |     3.22 |
| lgbm_morning        |     226 |     2.56 |
| chronos_morning     |     226 |     3.56 |
| ensemble_morning    |     226 |     2.83 |
| chronos_ft          |     226 |     2.92 |
| ensemble_ft         |     226 |     2.97 |
| ensemble_ft_morning |     226 |     2.43 |

## Probabilistic forecasts

| method                               |   mean pinball MW |   coverage 80 % (P10-P90) |   coverage 90 % (P5-P95) |   width 80 % MW |   median MAPE % |   hours |
|:-------------------------------------|------------------:|--------------------------:|-------------------------:|----------------:|----------------:|--------:|
| avg(LightGBM + conformal, Chronos-2) |            429.6  |                     72.12 |                    81.42 |         4256.36 |            2.99 |     226 |
| official + conformal (benchmark)     |            659.12 |                     65.49 |                    70.8  |         4203.56 |            3.9  |     226 |
