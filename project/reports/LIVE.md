# Live forecasts

On-time live forecasts with known actuals: 6 days. The pre-registered evaluation
(live/PREREGISTRATION.md) happens after at least 60 days.

## Point forecasts

| model               |   hours |   MAPE % |
|:--------------------|--------:|---------:|
| official            |     130 |     4.58 |
| official+bc         |     130 |     4.3  |
| lgbm                |     130 |     3.95 |
| chronos             |     130 |     4.46 |
| ensemble            |     130 |     3.83 |
| lgbm_morning        |     130 |     2.77 |
| chronos_morning     |     130 |     4.44 |
| ensemble_morning    |     130 |     3.34 |
| chronos_ft          |     130 |     3.65 |
| ensemble_ft         |     130 |     3.59 |
| ensemble_ft_morning |     130 |     2.78 |

## Probabilistic forecasts

| method                               |   mean pinball MW |   coverage 80 % (P10-P90) |   coverage 90 % (P5-P95) |   width 80 % MW |   median MAPE % |   hours |
|:-------------------------------------|------------------:|--------------------------:|-------------------------:|----------------:|----------------:|--------:|
| avg(LightGBM + conformal, Chronos-2) |            481.94 |                     68.46 |                    73.85 |         4378.46 |            3.19 |     130 |
| official + conformal (benchmark)     |            735.93 |                     62.31 |                    67.69 |         4261.73 |            4.16 |     130 |
