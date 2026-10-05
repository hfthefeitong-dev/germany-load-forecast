# Live forecasts

On-time live forecasts with known actuals: 4 days. The pre-registered evaluation
(live/PREREGISTRATION.md) happens after at least 60 days.

## Point forecasts

| model               |   hours |   MAPE % |
|:--------------------|--------:|---------:|
| official            |      82 |     6.05 |
| official+bc         |      82 |     5.59 |
| lgbm                |      82 |     4.31 |
| chronos             |      82 |     6.16 |
| ensemble            |      82 |     5.2  |
| lgbm_morning        |      82 |     3.44 |
| chronos_morning     |      82 |     6.23 |
| ensemble_morning    |      82 |     4.7  |
| chronos_ft          |      82 |     5.09 |
| ensemble_ft         |      82 |     4.68 |
| ensemble_ft_morning |      82 |     3.79 |

## Probabilistic forecasts

| method                               |   mean pinball MW |   coverage 80 % (P10-P90) |   coverage 90 % (P5-P95) |   width 80 % MW |   median MAPE % |   hours |
|:-------------------------------------|------------------:|--------------------------:|-------------------------:|----------------:|----------------:|--------:|
| avg(LightGBM + conformal, Chronos-2) |            627.07 |                     51.22 |                    59.76 |         4508    |            4.37 |      82 |
| official + conformal (benchmark)     |            996.54 |                     43.9  |                    48.78 |         4251.89 |            5.56 |      82 |
