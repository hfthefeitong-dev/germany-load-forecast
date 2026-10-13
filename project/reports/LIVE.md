# Live forecasts

On-time live forecasts with known actuals: 11 days. The pre-registered evaluation
(live/PREREGISTRATION.md) happens after at least 60 days.

## Point forecasts

| model               |   hours |   MAPE % |
|:--------------------|--------:|---------:|
| official            |     250 |     3.96 |
| official+bc         |     250 |     3.95 |
| lgbm                |     250 |     3.4  |
| chronos             |     250 |     3.7  |
| ensemble            |     250 |     3.3  |
| lgbm_morning        |     250 |     2.72 |
| chronos_morning     |     250 |     3.66 |
| ensemble_morning    |     250 |     3    |
| chronos_ft          |     250 |     3    |
| ensemble_ft         |     250 |     3.04 |
| ensemble_ft_morning |     250 |     2.6  |

## Probabilistic forecasts

| method                               |   mean pinball MW |   coverage 80 % (P10-P90) |   coverage 90 % (P5-P95) |   width 80 % MW |   median MAPE % |   hours |
|:-------------------------------------|------------------:|--------------------------:|-------------------------:|----------------:|----------------:|--------:|
| avg(LightGBM + conformal, Chronos-2) |            442.49 |                      70   |                     79.2 |         4256.76 |            3.02 |     250 |
| official + conformal (benchmark)     |            627.03 |                      67.6 |                     72.8 |         4201.86 |            3.74 |     250 |
