# Live forecasts

On-time live forecasts with known actuals: 40 days. The pre-registered evaluation
(live/PREREGISTRATION.md) happens after at least 60 days.

## Point forecasts

| model               |   hours |   MAPE % |
|:--------------------|--------:|---------:|
| official            |     947 |     3.62 |
| official+bc         |     947 |     2.8  |
| lgbm                |     947 |     2.53 |
| chronos             |     947 |     2.56 |
| ensemble            |     947 |     2.33 |
| lgbm_morning        |     947 |     2.23 |
| chronos_morning     |     947 |     2.37 |
| ensemble_morning    |     947 |     2.12 |
| chronos_ft          |     947 |     2.27 |
| ensemble_ft         |     947 |     2.24 |
| ensemble_ft_morning |     947 |     2.04 |

## Probabilistic forecasts

| method                               |   mean pinball MW |   coverage 80 % (P10-P90) |   coverage 90 % (P5-P95) |   width 80 % MW |   median MAPE % |   hours |
|:-------------------------------------|------------------:|--------------------------:|-------------------------:|----------------:|----------------:|--------:|
| avg(LightGBM + conformal, Chronos-2) |            354.63 |                     82.58 |                    89.76 |         4130.46 |            2.23 |     947 |
| official + conformal (benchmark)     |            485.4  |                     74.13 |                    83.32 |         4263.7  |            2.89 |     947 |
