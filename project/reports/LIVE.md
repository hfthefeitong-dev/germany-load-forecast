# Live forecasts

On-time live forecasts with known actuals: 39 days. The pre-registered evaluation
(live/PREREGISTRATION.md) happens after at least 60 days.

## Point forecasts

| model               |   hours |   MAPE % |
|:--------------------|--------:|---------:|
| official            |     923 |     3.58 |
| official+bc         |     923 |     2.78 |
| lgbm                |     923 |     2.53 |
| chronos             |     923 |     2.6  |
| ensemble            |     923 |     2.35 |
| lgbm_morning        |     923 |     2.24 |
| chronos_morning     |     923 |     2.41 |
| ensemble_morning    |     923 |     2.14 |
| chronos_ft          |     923 |     2.29 |
| ensemble_ft         |     923 |     2.25 |
| ensemble_ft_morning |     923 |     2.05 |

## Probabilistic forecasts

| method                               |   mean pinball MW |   coverage 80 % (P10-P90) |   coverage 90 % (P5-P95) |   width 80 % MW |   median MAPE % |   hours |
|:-------------------------------------|------------------:|--------------------------:|-------------------------:|----------------:|----------------:|--------:|
| avg(LightGBM + conformal, Chronos-2) |            356.87 |                     82.45 |                    89.49 |         4145.72 |            2.24 |     923 |
| official + conformal (benchmark)     |            479.68 |                     74.86 |                    83.97 |         4259.93 |            2.87 |     923 |
