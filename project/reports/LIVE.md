# Live forecasts

On-time live forecasts with known actuals: 28 days. The pre-registered evaluation
(live/PREREGISTRATION.md) happens after at least 60 days.

## Point forecasts

| model               |   hours |   MAPE % |
|:--------------------|--------:|---------:|
| official            |     659 |     3.25 |
| official+bc         |     659 |     2.86 |
| lgbm                |     659 |     2.39 |
| chronos             |     659 |     2.69 |
| ensemble            |     659 |     2.28 |
| lgbm_morning        |     659 |     2.15 |
| chronos_morning     |     659 |     2.53 |
| ensemble_morning    |     659 |     2.15 |
| chronos_ft          |     659 |     2.37 |
| ensemble_ft         |     659 |     2.2  |
| ensemble_ft_morning |     659 |     2    |

## Probabilistic forecasts

| method                               |   mean pinball MW |   coverage 80 % (P10-P90) |   coverage 90 % (P5-P95) |   width 80 % MW |   median MAPE % |   hours |
|:-------------------------------------|------------------:|--------------------------:|-------------------------:|----------------:|----------------:|--------:|
| avg(LightGBM + conformal, Chronos-2) |            344.48 |                     85.43 |                    90.9  |         4202.34 |            2.22 |     659 |
| official + conformal (benchmark)     |            475.53 |                     77.85 |                    83.92 |         4231.58 |            2.87 |     659 |
