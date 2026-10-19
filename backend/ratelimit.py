"""A small per-client rate limiter for the public parse endpoint.

Best effort by design. State lives in this process's memory, so on serverless hosting each warm instance counts
separately and the effective limit can be higher than configured; it stops a single client hammering one instance
and gives honest users a clear message, it does not replace a platform firewall (use the host's rate-limit rules
for hard guarantees). Memory is bounded: at most `max_clients` clients are tracked, least recently seen first out.
"""
from __future__ import annotations

import math
import os
import time
from collections import OrderedDict, deque
from typing import Callable

LOOPBACK = {"127.0.0.1", "::1", "localhost", "testclient"}


class RateLimiter:
    """Sliding-window log: at most `limit` requests per `window` seconds per key."""

    def __init__(self, limit: int, window: float = 60.0, max_clients: int = 5000, clock: Callable[[], float] = time.monotonic):
        self.limit, self.window, self.max_clients, self.clock = limit, window, max_clients, clock
        self._hits: OrderedDict[str, deque[float]] = OrderedDict()

    @property
    def enabled(self) -> bool:
        return self.limit > 0

    def check(self, key: str) -> tuple[bool, int]:
        """Record a request. Returns (allowed, seconds_until_a_slot_frees). A refused request is not recorded."""
        now = self.clock()
        hits = self._hits.pop(key, None) or deque()
        while hits and now - hits[0] >= self.window:
            hits.popleft()
        allowed = len(hits) < self.limit
        if allowed:
            hits.append(now)
        self._hits[key] = hits  # re-inserted last: most recently seen
        while len(self._hits) > self.max_clients:
            self._hits.popitem(last=False)
        retry = 0 if allowed else max(1, math.ceil(self.window - (now - hits[0])))
        return allowed, retry


def trust_proxy_headers() -> bool:
    """Only believe X-Forwarded-For behind a proxy that sets it: Vercel does, a bare server does not."""
    return bool(os.environ.get("VERCEL") or os.environ.get("WORDWORLD_TRUST_PROXY"))


def client_key(forwarded_for: str | None, peer: str | None, trust_proxy: bool) -> str:
    if trust_proxy and forwarded_for:
        first = forwarded_for.split(",")[0].strip()
        if first:
            return first[:64]
    return (peer or "unknown")[:64]


def from_environment() -> RateLimiter:
    """WORDWORLD_RATE_LIMIT requests per WORDWORLD_RATE_WINDOW seconds; 0 turns it off."""
    def number(name: str, default: float) -> float:
        try:
            return float(os.environ.get(name, default))
        except ValueError:
            return default
    return RateLimiter(int(number("WORDWORLD_RATE_LIMIT", 300)), number("WORDWORLD_RATE_WINDOW", 60))
