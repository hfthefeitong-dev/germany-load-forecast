# Pre-registration of the live forecast evaluation

Written and committed on 2026-09-25, before the first live forecast. The Git history of this repository timestamps every stored forecast.

## Setup

- Every day, on day D-1 before **12:00 Europe/Berlin** (day-ahead gate closure), `python -m loadfc live` forecasts every hour of day D and writes `live/forecasts/D.csv` plus a manifest `D.json`. `tools/run-live.ps1` commits and pushes both.
- A forecast counts only if its manifest says `"on_time": true`, i.e. the file was written before the deadline. Late or missing days are excluded, never filled in afterwards.
- All settings are frozen in `live/settings.json`, derived from the validation period of the main backtest window. Models are retrained monthly exactly as in the backtest: LightGBM on data up to the day before the month starts; Chronos-2 fine-tuned (LoRA, 500 steps) on the same data.
- No setting or model code is changed during the live period. A change that alters forecasts ends this live period and starts a new one with its own pre-registration.

## Hypotheses

| | Claim | Compared with |
|---|---|---|
| **H1 (primary)** | The ensemble (LightGBM + zero-shot Chronos-2, load up to D-2) has a lower MAPE | the official TSO forecast, and the official forecast + bias correction |
| H2 | Adding the load of D-1 until 08:00 lowers the error | the H1 ensemble |
| H3 | Fine-tuning Chronos-2 lowers the ensemble's error | the H1 ensemble |
| H4 | The probabilistic forecast, avg(LightGBM + conformal, Chronos-2), has a lower mean pinball loss, and its 80 % and 90 % intervals cover within ±5 percentage points of nominal | the official forecast + conformal intervals |

H2 and H3 are the two questions the backtest could not settle: H2 relies on a SMARD publication delay measured only once, and H3 failed the backtest decision rule because of short history.

## Evaluation

- **When:** once at least 60 on-time days with known actuals exist, and not before 2026-12-01. The interim report `reports/LIVE.md` is updated daily but is not the evaluation.
- **Metrics:** MAPE for point forecasts; mean pinball loss over P5, P10, P25, P50, P75, P90, P95 and interval coverage for probabilistic forecasts.
- **Significance:** Diebold-Mariano test on daily mean losses with a Newey-West variance (7 lags), two-sided, α = 0.05.
- **Reporting:** all four hypotheses are reported whatever the outcome.
