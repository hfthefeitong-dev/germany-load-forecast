# Beating Germany's official day-ahead load forecast, with less information

Day-ahead forecasts of electricity demand for Germany, benchmarked against the official forecast that the four transmission system operators (TSOs) publish every day. The models use **strictly less information** than the official forecaster. An ensemble of gradient boosting and a zero-shot foundation model is **about 30 % more accurate than the official forecast and beats it in every one of 21 test months**, across two separate out-of-sample periods. Forecast errors are then translated into **imbalance costs in euros** using the German imbalance price reBAP.

| MAPE | Main test: Oct 2025 – Sep 2026 | Backtest: Jan – Sep 2025 |
|---|---|---|
| Naive: same hour last week | 5.53 % | 4.90 % |
| **Official TSO forecast** | **3.84 %** | **3.83 %** |
| LightGBM | 2.97 % | 3.34 % *(not significant)* |
| Chronos-2, zero-shot foundation model | 3.01 % | 2.46 % |
| **Ensemble: LightGBM + Chronos-2** | **2.69 %** | **2.59 %** |
| Months in which the ensemble beats the official forecast | 12 of 12 | 9 of 9 |

Ensemble vs official: Diebold-Mariano p < 0.001 in both periods. Full tables: [`reports/RESULTS.md`](reports/RESULTS.md).

---

## The finding that started it

![Official forecast error vs sunshine](reports/figures/02_official_error_vs_sun.png)

At midday the official forecast's error rises almost linearly with solar radiation: it under-forecasts on dull days and over-forecasts by up to 20 % on sunny ones. The likely cause is **behind-the-meter rooftop PV**. When the sun shines, households and businesses consume their own solar power, and the load seen by the grid drops. The effect is strongest on weekends and public holidays, when baseline demand is low. On sunny weekend and holiday middays the official forecast's error is 8.6 % in the main test period and 9.5 % in the backtest; the ensemble's is 2.7 % and 3.4 %.

The largest official errors of the year were on **Sunday 26 April 2026** and **Labour Day, 1 May 2026**, both clear-sky days across all of Germany, with the forecast about 9 GW (24 %) too high.

![Week of 20 April 2026](reports/figures/04_week_sunny_sunday.png)

---

## Fairness: the comparison is only meaningful if the model cannot see the future

The official forecast for day D is published on day D-1 (by 18:00, per [SMARD](https://www.smard.de/page/en/wiki-article/5884/206318/forecast-data)). This project deliberately uses **less** than that:

| Information | Used for day D | Why it is fair |
|---|---|---|
| Actual load | only up to the end of day **D-2** | minimum lag is 48 h, never 24 h |
| Weather | forecasts issued **48 h** before each hour | not observed weather, which would leak the future |
| Calendar, holidays | any | known years in advance |
| Hyperparameters | chosen on a validation period **before** each test period | test data is never used for tuning |
| Model training | retrained monthly on data known at that time | the model never sees the month it predicts |

The rule is enforced by an automated test ([`tests/test_leakage.py`](tests/test_leakage.py)): it scrambles the load of days D-1 and D and asserts that the features for day D do not change, and a second test confirms that scrambling day D-2 *does* change them.

A trap avoided along the way: Open-Meteo's *Historical Forecast API* sounds right but stitches together the first few hours of each weather model run, i.e. forecasts with a lead time of only hours. This project uses the *Previous Runs API* with `_previous_day2`, the genuine 48 h-ahead forecast.

---

## Data

| Data | Source | Resolution |
|---|---|---|
| Actual grid load, official day-ahead load forecast, day-ahead price (DE-LU) | [SMARD](https://www.smard.de) (Bundesnetzagentur) | hourly |
| Temperature, solar radiation, cloud cover: 48 h-ahead forecasts for one city per federal state | [Open-Meteo Previous Runs API](https://open-meteo.com/en/docs/previous-runs-api) | hourly |
| Imbalance price reBAP, quality-assured | [netztransparenz.de](https://www.netztransparenz.de/de-de/Regelenergie/Ausgleichsenergiepreis/reBAP) | 15 min, averaged to hourly |
| Public holidays per federal state | [`holidays`](https://pypi.org/project/holidays/) package | daily |

All sources are free and need no registration. History starts in January 2024, when the weather forecast archive begins.

---

## Method

**Features** ([`features.py`](src/loadfc/features.py)). Hour, weekday, season; the *share of the population* on a public holiday (holidays differ by state, e.g. Epiphany only in BW, BY, ST); bridge days; the Christmas period; load 2, 7 and 14 days earlier; population-weighted temperature, radiation and cloud cover, plus radiation in the PV-heavy south.

**LightGBM** ([`models.py`](src/loadfc/models.py)). Gradient-boosted trees with an L1 objective, retrained at the start of every test month on all data known at that time. The number of trees is chosen by early stopping on the validation period.

**Chronos-2** ([`foundation.py`](src/loadfc/foundation.py)). Amazon's 120M-parameter time series foundation model (2025, Apache-2.0), used **zero-shot**: it has never been trained on German load. It receives the load history and the same known-future covariates as LightGBM. The context length (12 weeks or the maximum of about 11 months) is chosen on the validation period; both periods chose the longer one.

**Ensemble.** The plain average of LightGBM and Chronos-2. Equal weights involve no tuning, so evaluating it on the test periods stays fair.

**Two test periods.** Each has its own validation period, and every choice is frozen before its test period is touched:

| | Validation | Test | Training data at test start |
|---|---|---|---|
| Main | Jul – Sep 2025 | Oct 2025 – Sep 2026 | 20 months |
| Backtest | Oct – Dec 2024 | Jan – Sep 2025 | 11 months |

---

## Results

![Month-by-month error](reports/figures/07_monthly_mape.png)

**The ensemble is the only model that wins every month.** Each component fails somewhere:

- **LightGBM needs history.** At the start of the backtest it had less than a year of training data and almost no winter. The validation period stopped boosting after only 141 trees, and its January 2025 error was 6.5 %. Over the backtest its advantage over the official forecast is not statistically significant (p = 0.23). With 20 months of history in the main period it is strong.
- **Chronos-2 needs no training data but struggles with holidays.** Zero-shot, it is the best single model in the backtest. On public holidays, bridge days and at Christmas it is much worse than LightGBM, because holidays are rare in its context window. Even 8,192 hours (341 days) do not reach back to last year's Christmas.
- **Averaging them is the safe choice, not always the best one.** The ensemble beats both components in 13 of 21 months, and in the backtest Chronos-2 alone is slightly better overall. What the ensemble adds is robustness: the two models rarely fail in the same month, so the average never has a bad one.

![MAPE by situation, main test period](reports/figures/03_mape_by_segment.png)

| MAPE [%], main test period | Official | LightGBM | Chronos-2 | Ensemble |
|---|---|---|---|---|
| All hours | 3.84 | 2.97 | 3.01 | **2.69** |
| Working days | 3.51 | 2.81 | 2.83 | **2.58** |
| Weekends | 4.43 | 3.36 | 3.01 | **2.80** |
| Public holidays | 4.61 | **3.10** | 6.03 | 3.88 |
| Bridge days | 7.25 | **2.66** | 6.55 | 4.34 |
| Christmas period | 4.79 | **3.54** | 7.16 | 4.76 |
| Sunny off-day middays | 8.57 | 3.16 | 3.41 | **2.69** |

Public holidays remain the weak spot: in the backtest the ensemble's holiday error (6.0 %) is worse than the official forecast's (5.0 %).

### What drives LightGBM's improvement? (ablation, main period)

| MAPE [%] | All hours | Sunny off-day middays | Public holidays |
|---|---|---|---|
| Full model | 2.97 | 3.16 | 3.10 |
| without solar radiation & cloud | 3.15 | 3.89 | 3.78 |
| without any weather | 3.46 | 4.15 | 4.39 |
| without holiday detail | 3.02 | 3.53 | 4.07 |
| *Official forecast* | *3.84* | *8.57* | *4.61* |

Removing solar features hurts exactly where the PV hypothesis predicts. But even with **no weather at all**, LightGBM still beats the official forecast, so calendar handling and recent load level matter as much as sunshine.

---

## What are the errors worth?

A balance responsible party (BRP) buys its forecast F on the day-ahead market at price P_da. Actual demand turns out to be A, and the difference is settled at the imbalance price reBAP:

```
extra cost = (A − F) × (reBAP − P_da)
```

An error only costs money when the imbalance price moves away from the day-ahead price in the wrong direction. Treating the whole of Germany as one balancing group:

| Extra imbalance cost [million €] | Main | Main, excl. extreme hours* | Backtest | Backtest, excl. extreme hours* |
|---|---|---|---|---|
| Official forecast | 145 | 82 | 114 | 105 |
| LightGBM | **91** | 74 | 119 | 113 |
| Chronos-2 | 114 | 74 | **79** | **85** |
| Ensemble | 102 | 74 | 99 | 99 |

\* Excluding hours with |reBAP| > 1,000 €/MWh: 13 hours in the main period, 14 in the backtest. The main period uses Oct 2025 – Aug 2026, where quality-assured reBAP is available.

Three lessons:

1. **The ensemble is cheaper than the official forecast in both periods**, with and without extreme hours.
2. **The most accurate model is not reliably the cheapest.** In the main period the ensemble is most accurate but LightGBM is cheapest. In the backtest LightGBM is more accurate than the official forecast but costs more. Cost depends on whether errors coincide with system shortages, not only on their size. This motivates *value-oriented* forecasting, i.e. training on cost rather than on accuracy.
3. **Cost differences are dominated by a few extreme hours.** In the main period, 13 hours account for most of the gap between the official forecast and LightGBM.

This is a thought experiment, not a market simulation: if every BRP forecast better, the system imbalance and therefore reBAP itself would change.

---

## Limitations

- **21 test months in two periods.** More than one year, but the periods are consecutive and share most of their weather regime.
- **Public holidays** are still forecast worse than the official forecast when training history is short.
- **Weather is represented by one city per state.** Weighting radiation by installed PV capacity (from the Marktstammdatenregister) would model behind-the-meter PV more directly.
- **Actual load values may be revised** after first publication. The lag features use final values, which a real-time forecaster would only have in provisional form.
- **Point forecasts only.** A trader or BRP would also want uncertainty (quantiles); Chronos-2 produces them natively.
- **No gating between models.** Using LightGBM on holidays and the ensemble elsewhere looks attractive in the tables, but choosing that rule after seeing the test results would be overfitting. It would need its own validation period.

---

## Reproduce

Requires Python 3.12 and, for Chronos-2, a CUDA GPU (tested on an RTX 4090 under WSL2). Exact package versions are pinned in [`requirements-lock.txt`](requirements-lock.txt).

```bash
pip install -r requirements-lock.txt
pip install -e . --no-deps
python -m pytest                 # calendar and leakage tests
python -m loadfc download        # ~3 min, all raw data
python -m loadfc all             # ~5 min: LightGBM, ablation, Chronos-2, reports
```

`all` runs `run`, `ablation`, `chronos` and `summary` in order. Only `summary` writes to `reports/`, so the steps never overwrite each other.

```
src/loadfc/
  config.py       paths, evaluation windows, federal states
  smard.py        load, official forecast, day-ahead price
  weather.py      48 h-ahead weather forecasts, aggregation to national features
  rebap.py        imbalance price
  calendar_de.py  holiday share, bridge days, Christmas
  features.py     feature table and the fairness rule
  models.py       baselines, LightGBM with monthly retraining
  foundation.py   Chronos-2 zero-shot
  evaluate.py     metrics, segments, Diebold-Mariano test
  cost.py         imbalance cost
tests/            fairness and calendar tests
reports/          RESULTS.md, results.json, figures
```
