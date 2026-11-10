# Live forecasts

On-time live forecasts with known actuals: 37 days. The pre-registered evaluation
(live/PREREGISTRATION.md) happens after at least 60 days.

## Point forecasts

| model               |   hours |   MAPE % |
|:--------------------|--------:|---------:|
| official            |     874 |     3.42 |
| official+bc         |     874 |     2.72 |
| lgbm                |     874 |     2.5  |
| chronos             |     874 |     2.64 |
| ensemble            |     874 |     2.35 |
| lgbm_morning        |     874 |     2.25 |
| chronos_morning     |     874 |     2.44 |
| ensemble_morning    |     874 |     2.17 |
| chronos_ft          |     874 |     2.32 |
| ensemble_ft         |     874 |     2.25 |
| ensemble_ft_morning |     874 |     2.07 |

## Probabilistic forecasts

| method                               |   mean pinball MW |   coverage 80 % (P10-P90) |   coverage 90 % (P5-P95) |   width 80 % MW |   median MAPE % |   hours |
|:-------------------------------------|------------------:|--------------------------:|-------------------------:|----------------:|----------------:|--------:|
| avg(LightGBM + conformal, Chronos-2) |            357.97 |                     82.61 |                    89.13 |         4173.4  |            2.26 |     874 |
| official + conformal (benchmark)     |            457.92 |                     76.89 |                    85.7  |         4255.51 |            2.79 |     874 |
