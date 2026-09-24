# Beating Germany's official day-ahead load forecast, with less information

Day-ahead forecasts of electricity demand for Germany, benchmarked against the official forecast that the four transmission system operators (TSOs) publish every day. The model uses **strictly less information** than the official forecaster and is still **30 % more accurate** over a full out-of-sample year. Forecast errors are then translated into **imbalance costs in euros** using the German imbalance price reBAP.

| Test year: Oct 2025 – Sep 2026, 8,610 hours | MAPE | MAE [MW] |
|---|---|---|
| Naive: same hour last week | 5.53 % | 2,936 |
| **Official TSO forecast** | **3.84 %** | 2,032 |
| LightGBM (this project) | 2.97 % | 1,579 |
| Chronos-2, zero-shot foundation model | 3.00 % | 1,586 |
| **Ensemble: LightGBM + Chronos-2** | **2.68 %** | **1,423** |

All improvements over the official forecast are statistically significant (Diebold-Mariano test, p < 0.001).

---

## The finding that started it

![Official forecast error vs sunshine](reports/figures/02_official_error_vs_sun.png)

At midday the official forecast's error rises almost linearly with solar radiation: it under-forecasts on dull days and over-forecasts by up to 20 % on sunny ones. The likely cause is **behind-the-meter rooftop PV**. When the sun shines, households and businesses consume their own solar power, and the load seen by the grid drops. The effect is strongest on weekends and public holidays, when baseline demand is low.

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
| Model hyperparameters | chosen on Jul–Sep 2025 only | the test year is never used for tuning |
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

**LightGBM** ([`models.py`](src/loadfc/models.py)). Gradient-boosted trees with an L1 objective, retrained at the start of every test month on all data known at that time.

**Chronos-2** ([`foundation.py`](src/loadfc/foundation.py)). Amazon's 120M-parameter time series foundation model (2025, Apache-2.0), used **zero-shot**: it has never been trained on German load. It receives 12 weeks of load history and the same known-future covariates as LightGBM.

**Ensemble.** The plain average of LightGBM and Chronos-2. Equal weights involve no tuning, so evaluating it on the test year stays fair.

---

## Results

![MAPE by situation](reports/figures/03_mape_by_segment.png)

| MAPE [%] | Official | LightGBM | Chronos-2 | Ensemble |
|---|---|---|---|---|
| All hours | 3.84 | 2.97 | 3.00 | **2.68** |
| Working days | 3.51 | 2.81 | 2.79 | **2.55** |
| Weekends | 4.43 | 3.36 | 2.97 | **2.78** |
| Public holidays | 4.61 | **3.10** | 7.32 | 4.40 |
| Bridge days | 7.25 | **2.66** | 6.07 | 4.16 |
| Christmas period | 4.79 | **3.54** | 7.21 | 4.79 |
| Sunny off-day middays | 8.57 | 3.16 | 3.04 | **2.47** |

**LightGBM and Chronos-2 are complementary.** Overall they are statistically indistinguishable (p = 0.94). Chronos-2 is better on ordinary weekends and sunny days; LightGBM is far better on holidays, bridge days and Christmas. A foundation model reading 12 weeks of context has seen almost no holidays, while LightGBM learns them from two years of history. Averaging the two combines the strengths and is significantly better than either alone.

### What drives the improvement? (ablation, LightGBM)

| MAPE [%] | All hours | Sunny off-day middays | Public holidays |
|---|---|---|---|
| Full model | 2.97 | 3.16 | 3.10 |
| without solar radiation & cloud | 3.15 | 3.89 | 3.78 |
| without any weather | 3.46 | 4.15 | 4.39 |
| without holiday detail | 3.02 | 3.53 | 4.07 |
| *Official forecast* | *3.84* | *8.57* | *4.61* |

Removing solar features hurts exactly where the PV hypothesis predicts. But even with **no weather at all**, the model still beats the official forecast, so calendar handling and recent load level matter as much as sunshine.

---

## What are the errors worth?

A balance responsible party (BRP) buys its forecast F on the day-ahead market at price P_da. Actual demand turns out to be A, and the difference is settled at the imbalance price reBAP:

```
extra cost = (A − F) × (reBAP − P_da)
```

An error only costs money when the imbalance price moves away from the day-ahead price in the wrong direction. Treating the whole of Germany as one balancing group (Oct 2025 – Aug 2026, the period with quality-assured reBAP):

| Extra imbalance cost | All hours | Excluding 13 hours with \|reBAP\| > 1,000 €/MWh |
|---|---|---|
| Official forecast | €145 M | €82 M |
| LightGBM | **€91 M** | **€74 M** |
| Chronos-2 | €102 M | €86 M |
| Ensemble | €96 M | €80 M |

Two lessons:

1. **The most accurate model is not the cheapest.** The ensemble has the lowest MAPE, but LightGBM has the lowest cost. Cost depends on whether errors coincide with system shortages, not on their size. This motivates *value-oriented* forecasting, i.e. training on cost rather than on accuracy.
2. **The cost advantage is concentrated in a few extreme hours.** Thirteen hours with extreme imbalance prices account for most of the gap between the official forecast and LightGBM. Excluding them, the saving shrinks from 37 % to about 10 %. Thirteen hours are too few to call this a robust result.

This is a thought experiment, not a market simulation: if every BRP forecast better, the system imbalance and therefore reBAP itself would change.

---

## Limitations

- **One test year.** Results could differ in a year with an unusual winter or a different PV build-out.
- **Weather is represented by one city per state.** Weighting radiation by installed PV capacity (from the Marktstammdatenregister) would model behind-the-meter PV more directly.
- **Actual load values may be revised** after first publication. The lag features use final values, which a real-time forecaster would only have in provisional form.
- **Point forecasts only.** A trader or BRP would also want uncertainty (quantiles); Chronos-2 produces them natively.
- **No gating between models.** Using LightGBM on holidays and the ensemble elsewhere looks attractive in the table above, but choosing that rule after seeing the test results would be overfitting. It would need its own validation period.

---

## Reproduce

Requires Python 3.12 and, for Chronos-2, a CUDA GPU (tested on an RTX 4090).

```bash
pip install -e ".[dev]" "chronos-forecasting>=2.0" tabulate
python -m pytest                 # calendar and leakage tests
python -m loadfc download        # ~3 min, all raw data
python -m loadfc run             # features, LightGBM, baselines
python -m loadfc ablation        # feature-group ablation
python -m loadfc chronos         # Chronos-2 zero-shot, ~5 min on GPU
python -m loadfc summary         # final tables -> reports/RESULTS.md, figures
```

```
src/loadfc/
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
reports/          RESULTS.md, ablation, figures
```
