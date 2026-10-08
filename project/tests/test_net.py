"""Download retries: transient failures are retried, permanent ones are not."""

import pytest
import requests

from loadfc import net


class FakeResponse:
    def __init__(self, status=200, payload=None, bad_json=False):
        self.status_code = status
        self._payload = payload
        self._bad_json = bad_json

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}", response=self)

    def json(self):
        if self._bad_json:
            raise requests.exceptions.JSONDecodeError("Expecting ',' delimiter", "{", 1)
        return self._payload


def _patch(monkeypatch, responses):
    calls = []

    def fake_get(url, params=None, timeout=None):
        calls.append(url)
        r = responses[len(calls) - 1]
        if isinstance(r, Exception):
            raise r
        return r

    monkeypatch.setattr(net.requests, "get", fake_get)
    monkeypatch.setattr(net.time, "sleep", lambda s: None)
    return calls


def test_truncated_json_is_retried(monkeypatch):
    # The failure of 2026-10-08: a body that is not valid JSON.
    calls = _patch(monkeypatch, [FakeResponse(bad_json=True), FakeResponse(payload={"ok": 1})])
    assert net.get_json("http://x") == {"ok": 1}
    assert len(calls) == 2


def test_timeout_and_server_error_are_retried(monkeypatch):
    calls = _patch(monkeypatch, [requests.Timeout("slow"), FakeResponse(status=503), FakeResponse(payload=[1, 2])])
    assert net.get_json("http://x") == [1, 2]
    assert len(calls) == 3


def test_gives_up_after_three_attempts(monkeypatch):
    calls = _patch(monkeypatch, [FakeResponse(bad_json=True)] * 3)
    with pytest.raises(ValueError):
        net.get_json("http://x")
    assert len(calls) == 3


def test_not_found_is_not_retried(monkeypatch):
    calls = _patch(monkeypatch, [FakeResponse(status=404), FakeResponse(payload={})])
    with pytest.raises(requests.HTTPError):
        net.get_json("http://x")
    assert len(calls) == 1
