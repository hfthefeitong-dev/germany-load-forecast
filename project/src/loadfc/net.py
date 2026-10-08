"""HTTP download with retries.

Public data services occasionally answer with a timeout, a 5xx error or a
truncated body. On 2026-10-08 a truncated JSON reply from the weather API
made the 11:16 live run fail; the 11:41 backup run saved the day. Retrying
makes a single run robust against such hiccups. It changes when a download
succeeds, never what is downloaded, so forecasts are unaffected.
"""

import time

import requests

RETRY_WAIT_SECONDS = (5, 15)  # wait before the 2nd and 3rd attempt


def get_json(url: str, params: dict | None = None, timeout: int = 60):
    """GET `url` and parse JSON, trying up to three times.

    Retried: connection errors, timeouts, HTTP 429 and 5xx, and bodies that
    are not valid JSON. Other HTTP errors (e.g. 404) are raised at once,
    because repeating the request would not help.
    """
    attempts = len(RETRY_WAIT_SECONDS) + 1
    for attempt in range(attempts):
        try:
            r = requests.get(url, params=params, timeout=timeout)
            if r.status_code == 429 or r.status_code >= 500:
                raise requests.HTTPError(f"HTTP {r.status_code}", response=r)
            r.raise_for_status()
            return r.json()
        except (requests.ConnectionError, requests.Timeout, ValueError) as e:
            error = e  # ValueError covers requests' JSONDecodeError
        except requests.HTTPError as e:
            if e.response is not None and e.response.status_code != 429 and e.response.status_code < 500:
                raise
            error = e
        if attempt == attempts - 1:
            raise error
        wait = RETRY_WAIT_SECONDS[attempt]
        print(f"download failed ({type(error).__name__}: {str(error)[:80]}), retry in {wait} s", flush=True)
        time.sleep(wait)
