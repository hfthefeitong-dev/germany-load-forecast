# Live forecasts

On-time live forecasts with known actuals: 9 days. The pre-registered evaluation
(live/PREREGISTRATION.md) happens after at least 60 days.

## Point forecasts

| model               |   hours |   MAPE % |
|:--------------------|--------:|---------:|
| official            |     202 |     4.18 |
| official+bc         |     202 |     4.09 |
| lgbm                |     202 |     3.49 |
| chronos             |     202 |     3.66 |
| ensemble            |     202 |     3.3  |
| lgbm_morning        |     202 |     2.56 |
| chronos_morning     |     202 |     3.57 |
| ensemble_morning    |     202 |     2.85 |
| chronos_ft          |     202 |     3    |
| ensemble_ft         |     202 |     3.07 |
| ensemble_ft_morning |     202 |     2.43 |

## Probabilistic forecasts

| method                               |   mean pinball MW |   coverage 80 % (P10-P90) |   coverage 90 % (P5-P95) |   width 80 % MW |   median MAPE % |   hours |
|:-------------------------------------|------------------:|--------------------------:|-------------------------:|----------------:|----------------:|--------:|
| avg(LightGBM + conformal, Chronos-2) |            441.59 |                     70.79 |                    80.69 |         4268.73 |            3.08 |     202 |
| official + conformal (benchmark)     |            680.72 |                     65.84 |                    70.79 |         4210.77 |            4    |     202 |
