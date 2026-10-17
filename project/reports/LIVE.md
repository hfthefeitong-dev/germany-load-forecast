# Live forecasts

On-time live forecasts with known actuals: 14 days. The pre-registered evaluation
(live/PREREGISTRATION.md) happens after at least 60 days.

## Point forecasts

| model               |   hours |   MAPE % |
|:--------------------|--------:|---------:|
| official            |     322 |     3.48 |
| official+bc         |     322 |     3.48 |
| lgbm                |     322 |     2.85 |
| chronos             |     322 |     3.09 |
| ensemble            |     322 |     2.73 |
| lgbm_morning        |     322 |     2.34 |
| chronos_morning     |     322 |     3.02 |
| ensemble_morning    |     322 |     2.5  |
| chronos_ft          |     322 |     2.5  |
| ensemble_ft         |     322 |     2.51 |
| ensemble_ft_morning |     322 |     2.16 |

## Probabilistic forecasts

| method                               |   mean pinball MW |   coverage 80 % (P10-P90) |   coverage 90 % (P5-P95) |   width 80 % MW |   median MAPE % |   hours |
|:-------------------------------------|------------------:|--------------------------:|-------------------------:|----------------:|----------------:|--------:|
| avg(LightGBM + conformal, Chronos-2) |            378.92 |                     79.5  |                    87.27 |         4230    |            2.55 |     322 |
| official + conformal (benchmark)     |            546.04 |                     74.22 |                    78.26 |         4181.11 |            3.29 |     322 |
