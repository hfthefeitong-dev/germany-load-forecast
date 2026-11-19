# Live forecasts

On-time live forecasts with known actuals: 45 days. The pre-registered evaluation
(live/PREREGISTRATION.md) happens after at least 60 days.

## Point forecasts

| model               |   hours |   MAPE % |
|:--------------------|--------:|---------:|
| official            |    1067 |     3.47 |
| official+bc         |    1067 |     2.94 |
| lgbm                |    1067 |     2.56 |
| chronos             |    1067 |     2.55 |
| ensemble            |    1067 |     2.36 |
| lgbm_morning        |    1067 |     2.23 |
| chronos_morning     |    1067 |     2.4  |
| ensemble_morning    |    1067 |     2.15 |
| chronos_ft          |    1067 |     2.35 |
| ensemble_ft         |    1067 |     2.29 |
| ensemble_ft_morning |    1067 |     2.08 |

## Probabilistic forecasts

| method                               |   mean pinball MW |   coverage 80 % (P10-P90) |   coverage 90 % (P5-P95) |   width 80 % MW |   median MAPE % |   hours |
|:-------------------------------------|------------------:|--------------------------:|-------------------------:|----------------:|----------------:|--------:|
| avg(LightGBM + conformal, Chronos-2) |            368.61 |                     81.07 |                    88.57 |         4112.77 |            2.3  |    1067 |
| official + conformal (benchmark)     |            487.93 |                     73.76 |                    83.22 |         4289.06 |            2.92 |    1067 |
