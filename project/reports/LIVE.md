# Live forecasts

On-time live forecasts with known actuals: 53 days. The pre-registered evaluation
(live/PREREGISTRATION.md) happens after at least 60 days.

## Point forecasts

| model               |   hours |   MAPE % |
|:--------------------|--------:|---------:|
| official            |    1259 |     3.58 |
| official+bc         |    1259 |     3.05 |
| lgbm                |    1259 |     2.62 |
| chronos             |    1259 |     2.56 |
| ensemble            |    1259 |     2.39 |
| lgbm_morning        |    1211 |     2.14 |
| chronos_morning     |    1211 |     2.31 |
| ensemble_morning    |    1211 |     2.06 |
| chronos_ft          |    1259 |     2.23 |
| ensemble_ft         |    1259 |     2.26 |
| ensemble_ft_morning |    1211 |     1.98 |

## Probabilistic forecasts

| method                               |   mean pinball MW |   coverage 80 % (P10-P90) |   coverage 90 % (P5-P95) |   width 80 % MW |   median MAPE % |   hours |
|:-------------------------------------|------------------:|--------------------------:|-------------------------:|----------------:|----------------:|--------:|
| avg(LightGBM + conformal, Chronos-2) |            387.58 |                     79.43 |                    86.97 |         4133.56 |            2.34 |    1259 |
| official + conformal (benchmark)     |            502.47 |                     71.09 |                    81.02 |         4324.56 |            2.98 |    1259 |
