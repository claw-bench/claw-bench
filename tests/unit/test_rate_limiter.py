"""Tests for the token-bucket rate limiter."""

import time
import threading

from claw_bench.core.rate_limiter import (
    TokenBucket,
    RateLimiterRegistry,
    detect_provider,
)


class TestTokenBucket:
    def test_acquire_within_capacity(self):
        bucket = TokenBucket(rate=10.0, capacity=10.0)
        assert bucket.acquire(1) is True

    def test_acquire_exhausts_capacity(self):
        bucket = TokenBucket(rate=1.0, capacity=3.0)
        assert bucket.acquire(3) is True
        # Bucket is now empty — next acquire with short timeout should fail
        assert bucket.acquire(1, timeout=0.05) is False

    def test_refill_over_time(self):
        bucket = TokenBucket(rate=100.0, capacity=10.0)
        bucket.acquire(10)  # drain
        time.sleep(0.15)  # refill ~15 tokens, capped at 10
        assert bucket.acquire(5) is True

    def test_timeout_returns_false(self):
        bucket = TokenBucket(rate=0.1, capacity=1.0)
        bucket.acquire(1)
        start = time.monotonic()
        result = bucket.acquire(1, timeout=0.1)
        elapsed = time.monotonic() - start
        assert result is False
        assert elapsed < 0.5  # Should not block forever

    def test_thread_safety(self):
        bucket = TokenBucket(rate=1000.0, capacity=100.0)
        results = []

        def worker():
            for _ in range(10):
                results.append(bucket.acquire(1))

        threads = [threading.Thread(target=worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 100
        assert all(r is True for r in results)


class TestRateLimiterRegistry:
    def test_get_returns_bucket(self):
        reg = RateLimiterRegistry()
        b = reg.get("openai")
        assert isinstance(b, TokenBucket)

    def test_same_provider_returns_same_bucket(self):
        reg = RateLimiterRegistry()
        b1 = reg.get("openai")
        b2 = reg.get("openai")
        assert b1 is b2

    def test_configure_overrides(self):
        reg = RateLimiterRegistry()
        reg.configure("custom", rate=5.0, capacity=10.0)
        b = reg.get("custom")
        assert b.rate == 5.0
        assert b.capacity == 10.0

    def test_unknown_provider_uses_default(self):
        reg = RateLimiterRegistry()
        b = reg.get("unknown_provider_xyz")
        assert b.rate == 20.0  # default rate


class TestDetectProvider:
    def test_openai(self):
        assert detect_provider("https://api.openai.com/v1") == "openai"

    def test_anthropic(self):
        assert detect_provider("https://api.anthropic.com/v1") == "anthropic"

    def test_infini(self):
        assert detect_provider("https://cloud.infini-ai.com/maas/v1") == "infini"

    def test_unknown(self):
        assert detect_provider("https://some-random-api.com/v1") == "default"
