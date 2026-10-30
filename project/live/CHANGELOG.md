# Changes during the live period

The pre-registration allows no change that alters forecasts. Changes that only affect robustness or scheduling are listed here, with the evidence that forecasts are unaffected.

## 2026-10-30: deadline on DST days

- **What:** the 12:00 deadline is now wall-clock time on the issue day, and the check whether day D-2 is complete finds the previous calendar day the same way (`_deadline` and `_previous_day` in `src/loadfc/live.py`, tests in `tests/test_live_deadline.py`).
- **Why:** the old code added 12 hours to local midnight. On 2026-10-25, the day the clocks went back, that is 11:00, so the forecast for 2026-10-26, issued at 11:17 (commit b8e0434), was marked `"on_time": false`. In spring the deadline would have been 13:00. The same arithmetic made the manifest for 2026-10-27 report `"yesterday_complete (day D-2)": false`; that flag is only recorded and selects no variant.
- **2026-10-26 stays excluded.** The pre-registration counts a forecast only if its manifest says `"on_time": true`, and manifests are never changed. Admitting the day now, with its actuals known, would change the evaluation after seeing the data, so it stays out although it was issued before 12:00.
- **Forecasts unaffected:** the code before and after the change, run back to back on identical data without downloads, gave identical forecasts for 2026-10-31 (maximum difference 0.0 MW over all variants and quantiles). A dry run at 16:07 with freshly downloaded data differed from the forecast issued at 11:17 by up to 148 MW (0.3 %, zero-shot Chronos-2); since both code versions agree on the same data, that difference comes from the newer input data, not from the change.

## 2026-10-08: download retries

- **What:** SMARD and weather downloads now retry up to three times (waits of 5 s and 15 s) on timeouts, connection errors, HTTP 429/5xx and bodies that are not valid JSON (`src/loadfc/net.py`).
- **Why:** on 2026-10-08 the weather API returned a truncated JSON body and the 11:16 run failed. The 11:41 backup run issued the forecast on time.
- **Forecasts unaffected:** a dry run after the change reproduced the forecast issued that morning for 2026-10-09 exactly for every variant that uses load up to D-2 (maximum difference 0.0 MW). The morning variants differed by at most 17 MW (0.03 %), most likely because SMARD had revised that morning's provisional load values in the meantime.

## 2026-09-30: scheduling and locking

- **What:** the daily run moved from 09:46 to 11:16 with a backup run at 11:41, because scheduled runs are skipped while the computer is asleep. A lock file ensures that only one process issues the forecast for a given day.
- **Forecasts unaffected:** scheduling only. The first on-time live forecast (for 2026-10-02) was issued after this change.
