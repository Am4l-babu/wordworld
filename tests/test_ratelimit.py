"""The parse endpoint's rate limiter: exact sliding-window behaviour, bounded memory, and the HTTP contract."""
import pytest
from backend import main, ratelimit
from backend.ratelimit import RateLimiter, client_key
from tests.test_api import request


class Clock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


def test_the_window_slides_and_a_refused_request_is_not_counted():
    clock = Clock()
    limiter = RateLimiter(3, 60, clock=clock)
    assert [limiter.check("a")[0] for _ in range(3)] == [True, True, True]
    allowed, retry = limiter.check("a")
    assert not allowed and retry == 60
    clock.now += 59
    assert limiter.check("a") == (False, 1)          # still full; the refused attempts did not extend the block
    clock.now += 1
    assert limiter.check("a")[0] is True             # the first hit has aged out
    assert limiter.check("b")[0] is True             # other clients are unaffected


def test_a_limit_of_zero_disables_the_limiter():
    assert RateLimiter(0).enabled is False and RateLimiter(5).enabled is True


def test_memory_is_bounded_by_dropping_the_least_recently_seen_clients():
    limiter = RateLimiter(1, 60, max_clients=3, clock=Clock())
    for key in "abcd":
        limiter.check(key)
    assert list(limiter._hits) == ["b", "c", "d"]
    limiter.check("b")                                # touching b makes it the most recent
    limiter.check("e")
    assert list(limiter._hits) == ["d", "b", "e"]


@pytest.mark.parametrize("forwarded,peer,trust,expected", [
    ("203.0.113.9, 10.0.0.1", "10.0.0.2", True, "203.0.113.9"),
    ("203.0.113.9", "10.0.0.2", False, "10.0.0.2"),     # a bare server must not believe a client-supplied header
    (None, "10.0.0.2", True, "10.0.0.2"),
    ("", None, True, "unknown"),
    ("x" * 500, None, True, "x" * 64),
])
def test_the_client_key_trusts_forwarded_headers_only_behind_a_proxy(forwarded, peer, trust, expected):
    assert client_key(forwarded, peer, trust) == expected


def test_environment_configuration(monkeypatch):
    monkeypatch.setenv("WORDWORLD_RATE_LIMIT", "7")
    monkeypatch.setenv("WORDWORLD_RATE_WINDOW", "30")
    limiter = ratelimit.from_environment()
    assert (limiter.limit, limiter.window) == (7, 30)
    monkeypatch.setenv("WORDWORLD_RATE_LIMIT", "not a number")
    assert ratelimit.from_environment().limit == 300
    monkeypatch.delenv("WORDWORLD_RATE_LIMIT")
    assert ratelimit.from_environment().limit == 300


def test_over_the_limit_returns_429_json_with_retry_after_and_other_routes_are_untouched(monkeypatch):
    monkeypatch.setattr(main, "limiter", RateLimiter(2, 60, clock=Clock()))
    monkeypatch.setattr(main, "LOOPBACK", set())
    monkeypatch.setenv("VERCEL", "1")
    headers = {"x-forwarded-for": "198.51.100.7"}
    body = {"text": "Add a tree"}
    assert [request("POST", "/api/parse", json=body, headers=headers).status_code for _ in range(2)] == [200, 200]
    limited = request("POST", "/api/parse", json=body, headers=headers)
    assert limited.status_code == 429 and limited.headers["retry-after"] == "60"
    assert limited.headers["content-type"].startswith("application/json") and "Too many requests" in limited.json()["detail"]
    assert request("POST", "/api/parse", json=body, headers={"x-forwarded-for": "198.51.100.8"}).status_code == 200
    assert request("GET", "/api/health", headers=headers).status_code == 200
    assert request("GET", "/api/extractors", headers=headers).status_code == 200


def test_loopback_clients_are_never_limited(monkeypatch):
    monkeypatch.setattr(main, "limiter", RateLimiter(1, 60, clock=Clock()))
    assert [request("POST", "/api/parse", json={"text": "Add a tree"}).status_code for _ in range(5)] == [200] * 5
