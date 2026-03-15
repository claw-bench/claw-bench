"""Token-bucket rate limiter for LLM API calls.

Prevents hitting provider rate limits when many users run benchmarks
concurrently.  Each provider/model pair gets its own bucket.
"""

from __future__ import annotations

import asyncio
import time
import threading
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class TokenBucket:
    """Classic token-bucket rate limiter."""

    rate: float  # tokens added per second
    capacity: float  # max burst size
    _tokens: float = field(init=False)
    _last: float = field(init=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False)

    def __post_init__(self) -> None:
        self._tokens = self.capacity
        self._last = time.monotonic()

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last
        self._tokens = min(self.capacity, self._tokens + elapsed * self.rate)
        self._last = now

    def acquire(self, tokens: int = 1, timeout: float = 60.0) -> bool:
        """Block until *tokens* are available.  Returns False on timeout."""
        deadline = time.monotonic() + timeout
        with self._lock:
            while True:
                self._refill()
                if self._tokens >= tokens:
                    self._tokens -= tokens
                    return True
                wait = (tokens - self._tokens) / self.rate
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    return False
                # Release lock while sleeping
                self._lock.release()
                try:
                    time.sleep(min(wait, remaining, 0.5))
                finally:
                    self._lock.acquire()

    async def async_acquire(self, tokens: int = 1, timeout: float = 60.0) -> bool:
        """Async version — yields to event loop while waiting."""
        deadline = time.monotonic() + timeout
        while True:
            with self._lock:
                self._refill()
                if self._tokens >= tokens:
                    self._tokens -= tokens
                    return True
                wait = (tokens - self._tokens) / self.rate
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return False
            await asyncio.sleep(min(wait, remaining, 0.25))


# ── Default rate limit presets per provider ──────────────────────────

_PROVIDER_LIMITS: Dict[str, Dict[str, float]] = {
    "openai": {"rate": 50.0, "capacity": 100.0},  # 50 req/s burst 100
    "anthropic": {"rate": 40.0, "capacity": 80.0},
    "deepseek": {"rate": 30.0, "capacity": 60.0},
    "infini": {"rate": 20.0, "capacity": 40.0},
    "google": {"rate": 30.0, "capacity": 60.0},
    "default": {"rate": 20.0, "capacity": 40.0},
}


class RateLimiterRegistry:
    """Global registry of per-provider rate limiters."""

    def __init__(self) -> None:
        self._buckets: Dict[str, TokenBucket] = {}
        self._lock = threading.Lock()

    def get(self, provider: str) -> TokenBucket:
        with self._lock:
            if provider not in self._buckets:
                cfg = _PROVIDER_LIMITS.get(provider, _PROVIDER_LIMITS["default"])
                self._buckets[provider] = TokenBucket(
                    rate=cfg["rate"], capacity=cfg["capacity"]
                )
            return self._buckets[provider]

    def configure(self, provider: str, rate: float, capacity: float) -> None:
        """Override rate limit for a provider."""
        with self._lock:
            self._buckets[provider] = TokenBucket(rate=rate, capacity=capacity)


# Singleton
rate_limiters = RateLimiterRegistry()


def detect_provider(base_url: str) -> str:
    """Guess provider name from API base URL."""
    url = base_url.lower()
    for name in ("openai", "anthropic", "deepseek", "infini", "google"):
        if name in url:
            return name
    return "default"
