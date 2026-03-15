"""Tests for the result cache."""

import tempfile
from pathlib import Path

from claw_bench.core.cache import CacheKey, ResultCache, compute_content_hash


class TestCacheKey:
    def test_key_str(self):
        key = CacheKey("cal-001", "gpt-4.1", "vanilla", "abcdef123456789")
        assert key.key_str == "cal-001:gpt-4.1:vanilla:abcdef123456"

    def test_frozen(self):
        key = CacheKey("cal-001", "gpt-4.1", "vanilla", "abc")
        # Should be hashable (frozen dataclass)
        d = {key: "value"}
        assert d[key] == "value"


class TestResultCache:
    def test_put_and_get(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = ResultCache(cache_dir=Path(tmp), max_memory_entries=100)
            key = CacheKey("task-1", "model-1", "vanilla", "hash1")
            cache.put(key, {"score": 0.9, "passed": True})
            result = cache.get(key)
            assert result is not None
            assert result["score"] == 0.9

    def test_miss_returns_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = ResultCache(cache_dir=Path(tmp))
            key = CacheKey("nonexistent", "model", "vanilla", "hash")
            assert cache.get(key) is None

    def test_disabled_cache(self):
        cache = ResultCache(enabled=False)
        key = CacheKey("task", "model", "vanilla", "hash")
        cache.put(key, {"score": 1.0})
        assert cache.get(key) is None

    def test_disk_persistence(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache_dir = Path(tmp)

            # Write with one instance
            c1 = ResultCache(cache_dir=cache_dir)
            key = CacheKey("task-1", "model-1", "vanilla", "hash1")
            c1.put(key, {"score": 0.8})

            # Read with a fresh instance (empty memory)
            c2 = ResultCache(cache_dir=cache_dir)
            result = c2.get(key)
            assert result is not None
            assert result["score"] == 0.8

    def test_invalidate_all(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = ResultCache(cache_dir=Path(tmp))
            for i in range(5):
                key = CacheKey(f"task-{i}", "model", "vanilla", f"hash{i}")
                cache.put(key, {"score": i})
            count = cache.invalidate()
            assert count >= 5

    def test_invalidate_by_task(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = ResultCache(cache_dir=Path(tmp))
            k1 = CacheKey("task-a", "model", "vanilla", "h1")
            k2 = CacheKey("task-b", "model", "vanilla", "h2")
            cache.put(k1, {"score": 1})
            cache.put(k2, {"score": 2})
            cache.invalidate("task-a")
            assert cache.get(k1) is None
            assert cache.get(k2) is not None

    def test_stats(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = ResultCache(cache_dir=Path(tmp))
            key = CacheKey("t", "m", "v", "h")
            cache.put(key, {"x": 1})
            cache.get(key)  # hit
            cache.get(CacheKey("miss", "m", "v", "h"))  # miss
            stats = cache.stats
            assert stats["hits"] >= 1
            assert stats["misses"] >= 1
            assert stats["stores"] >= 1

    def test_eviction(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = ResultCache(cache_dir=Path(tmp), max_memory_entries=3)
            for i in range(5):
                key = CacheKey(f"task-{i}", "m", "v", f"h{i}")
                cache.put(key, {"i": i})
            assert cache.stats["evictions"] >= 2


class TestComputeContentHash:
    def test_stable_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            task_dir = Path(tmp)
            (task_dir / "instruction.md").write_text("Do something")
            h1 = compute_content_hash(task_dir)
            h2 = compute_content_hash(task_dir)
            assert h1 == h2
            assert len(h1) == 64  # SHA-256

    def test_different_content_different_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            task_dir = Path(tmp)
            (task_dir / "instruction.md").write_text("Task A")
            h1 = compute_content_hash(task_dir)
            (task_dir / "instruction.md").write_text("Task B")
            h2 = compute_content_hash(task_dir)
            assert h1 != h2

    def test_empty_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            h = compute_content_hash(Path(tmp))
            assert len(h) == 64
