# Live forecasts

On-time live forecasts with known actuals: 51 days. The pre-registered evaluation
(live/PREREGISTRATION.md) happens after at least 60 days.

## Point forecasts

| model               |   hours |   MAPE % |
|:--------------------|--------:|---------:|
| official            |    1211 |     3.53 |
| official+bc         |    1211 |     3.06 |
| lgbm                |    1211 |     2.6  |
| chronos             |    1211 |     2.58 |
| ensemble            |    1211 |     2.39 |
| lgbm_morning        |    1177 |     2.14 |
| chronos_morning     |    1177 |     2.33 |
| ensemble_morning    |    1177 |     2.08 |
| chronos_ft          |    1211 |     2.28 |
| ensemble_ft         |    1211 |     2.27 |
| ensemble_ft_morning |    1177 |     2    |

## Probabilistic forecasts

| method                               |   mean pinball MW |   coverage 80 % (P10-P90) |   coverage 90 % (P5-P95) |   width 80 % MW |   median MAPE % |   hours |
|:-------------------------------------|------------------:|--------------------------:|-------------------------:|----------------:|----------------:|--------:|
| avg(LightGBM + conformal, Chronos-2) |            383.61 |                     79.77 |                    87.28 |         4123.53 |            2.34 |    1211 |
| official + conformal (benchmark)     |            504.68 |                     71.18 |                    80.92 |         4309.47 |            2.98 |    1211 |
