# Live forecasts

On-time live forecasts with known actuals: 12 days. The pre-registered evaluation
(live/PREREGISTRATION.md) happens after at least 60 days.

## Point forecasts

| model               |   hours |   MAPE % |
|:--------------------|--------:|---------:|
| official            |     288 |     3.62 |
| official+bc         |     288 |     3.68 |
| lgbm                |     288 |     3.02 |
| chronos             |     288 |     3.22 |
| ensemble            |     288 |     2.89 |
| lgbm_morning        |     288 |     2.42 |
| chronos_morning     |     288 |     3.18 |
| ensemble_morning    |     288 |     2.62 |
| chronos_ft          |     288 |     2.61 |
| ensemble_ft         |     288 |     2.66 |
| ensemble_ft_morning |     288 |     2.27 |

## Probabilistic forecasts

| method                               |   mean pinball MW |   coverage 80 % (P10-P90) |   coverage 90 % (P5-P95) |   width 80 % MW |   median MAPE % |   hours |
|:-------------------------------------|------------------:|--------------------------:|-------------------------:|----------------:|----------------:|--------:|
| avg(LightGBM + conformal, Chronos-2) |            392.15 |                     77.78 |                    85.76 |         4260.48 |            2.63 |     288 |
| official + conformal (benchmark)     |            580.45 |                     71.18 |                    75.69 |         4200.42 |            3.47 |     288 |
