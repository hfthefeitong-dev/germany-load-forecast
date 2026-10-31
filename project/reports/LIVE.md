# Live forecasts

On-time live forecasts with known actuals: 27 days. The pre-registered evaluation
(live/PREREGISTRATION.md) happens after at least 60 days.

## Point forecasts

| model               |   hours |   MAPE % |
|:--------------------|--------:|---------:|
| official            |     635 |     3.27 |
| official+bc         |     635 |     2.84 |
| lgbm                |     635 |     2.41 |
| chronos             |     635 |     2.69 |
| ensemble            |     635 |     2.3  |
| lgbm_morning        |     635 |     2.13 |
| chronos_morning     |     635 |     2.52 |
| ensemble_morning    |     635 |     2.13 |
| chronos_ft          |     635 |     2.37 |
| ensemble_ft         |     635 |     2.21 |
| ensemble_ft_morning |     635 |     1.97 |

## Probabilistic forecasts

| method                               |   mean pinball MW |   coverage 80 % (P10-P90) |   coverage 90 % (P5-P95) |   width 80 % MW |   median MAPE % |   hours |
|:-------------------------------------|------------------:|--------------------------:|-------------------------:|----------------:|----------------:|--------:|
| avg(LightGBM + conformal, Chronos-2) |            345.45 |                     85.04 |                    90.71 |         4179.53 |            2.23 |     635 |
| official + conformal (benchmark)     |            478.36 |                     77.95 |                    83.94 |         4228.32 |            2.87 |     635 |
