# Live forecasts

On-time live forecasts with known actuals: 8 days. The pre-registered evaluation
(live/PREREGISTRATION.md) happens after at least 60 days.

## Point forecasts

| model               |   hours |   MAPE % |
|:--------------------|--------:|---------:|
| official            |     180 |     3.95 |
| official+bc         |     180 |     3.71 |
| lgbm                |     180 |     3.5  |
| chronos             |     180 |     3.7  |
| ensemble            |     180 |     3.3  |
| lgbm_morning        |     180 |     2.61 |
| chronos_morning     |     180 |     3.71 |
| ensemble_morning    |     180 |     2.93 |
| chronos_ft          |     180 |     3.05 |
| ensemble_ft         |     180 |     3.09 |
| ensemble_ft_morning |     180 |     2.49 |

## Probabilistic forecasts

| method                               |   mean pinball MW |   coverage 80 % (P10-P90) |   coverage 90 % (P5-P95) |   width 80 % MW |   median MAPE % |   hours |
|:-------------------------------------|------------------:|--------------------------:|-------------------------:|----------------:|----------------:|--------:|
| avg(LightGBM + conformal, Chronos-2) |            439.35 |                     72.78 |                    79.44 |         4294.57 |            2.94 |     180 |
| official + conformal (benchmark)     |            640.08 |                     67.78 |                    72.78 |         4217.9  |            3.65 |     180 |
