# Changes during the live period

The pre-registration allows no change that alters forecasts. Changes that only affect robustness or scheduling are listed here, with the evidence that forecasts are unaffected.

## 2026-10-08: download retries

- **What:** SMARD and weather downloads now retry up to three times (waits of 5 s and 15 s) on timeouts, connection errors, HTTP 429/5xx and bodies that are not valid JSON (`src/loadfc/net.py`).
- **Why:** on 2026-10-08 the weather API returned a truncated JSON body and the 11:16 run failed. The 11:41 backup run issued the forecast on time.
- **Forecasts unaffected:** a dry run after the change reproduced the forecast issued that morning for 2026-10-09 exactly for every variant that uses load up to D-2 (maximum difference 0.0 MW). The morning variants differed by at most 17 MW (0.03 %), most likely because SMARD had revised that morning's provisional load values in the meantime.

## 2026-09-30: scheduling and locking

- **What:** the daily run moved from 09:46 to 11:16 with a backup run at 11:41, because scheduled runs are skipped while the computer is asleep. A lock file ensures that only one process issues the forecast for a given day.
- **Forecasts unaffected:** scheduling only. The first on-time live forecast (for 2026-10-02) was issued after this change.
