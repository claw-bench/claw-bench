"""Result cache for benchmark task executions.

Caches results keyed by (task_id, model, skills_mode, content_hash) so
identical re-runs skip the expensive LLM API call.  Useful when 200
concurrent users may run overlapping task sets.
"""

from __future__ import annotations

import hashlib
import json
import logging
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CacheKey:
    task_id: str
    model: str
    skills_mode: str
    content_hash: str  # SHA-256 of instruction + environment data

    @property
    def key_str(self) -> str:
        return (
            f"{self.task_id}:{self.model}:{self.skills_mode}:{self.content_hash[:12]}"
        )


@dataclass
class CacheEntry:
    result: Dict[str, Any]
    created_at: float
    hit_count: int = 0


class ResultCache:
    """Thread-safe in-memory + on-disk result cache.

    Two layers:
    - L1: In-memory dict (fast, bounded by max_memory_entries)
    - L2: On-disk JSON files (persistent across restarts)
    """

    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        max_memory_entries: int = 5000,
        ttl_seconds: float = 3600 * 24,  # 24 hours
        enabled: bool = True,
    ) -> None:
        self.enabled = enabled
        self.cache_dir = cache_dir or Path.home() / ".claw-bench" / "cache"
        self.max_memory_entries = max_memory_entries
        self.ttl_seconds = ttl_seconds

        self._memory: Dict[str, CacheEntry] = {}
        self._lock = threading.Lock()
        self._stats = {"hits": 0, "misses": 0, "stores": 0, "evictions": 0}

        if self.enabled:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

    # ── Public API ──────────────────────────────────────────────────

    def get(self, key: CacheKey) -> Optional[Dict[str, Any]]:
        """Look up a cached result.  Returns None on miss."""
        if not self.enabled:
            return None

        ks = key.key_str

        # L1 — memory
        with self._lock:
            entry = self._memory.get(ks)
            if entry and (time.time() - entry.created_at) < self.ttl_seconds:
                entry.hit_count += 1
                self._stats["hits"] += 1
                return entry.result

        # L2 — disk
        disk_path = self._disk_path(ks)
        if disk_path.exists():
            try:
                data = json.loads(disk_path.read_text())
                if (time.time() - data.get("created_at", 0)) < self.ttl_seconds:
                    result = data["result"]
                    self._promote_to_memory(ks, result, data["created_at"])
                    with self._lock:
                        self._stats["hits"] += 1
                    return result
                else:
                    disk_path.unlink(missing_ok=True)
            except (json.JSONDecodeError, KeyError):
                disk_path.unlink(missing_ok=True)

        with self._lock:
            self._stats["misses"] += 1
        return None

    def put(self, key: CacheKey, result: Dict[str, Any]) -> None:
        """Store a result in the cache."""
        if not self.enabled:
            return

        ks = key.key_str
        now = time.time()

        # L1
        with self._lock:
            if len(self._memory) >= self.max_memory_entries:
                self._evict_oldest()
            self._memory[ks] = CacheEntry(result=result, created_at=now)
            self._stats["stores"] += 1

        # L2
        disk_path = self._disk_path(ks)
        try:
            disk_path.parent.mkdir(parents=True, exist_ok=True)
            disk_path.write_text(
                json.dumps(
                    {
                        "result": result,
                        "created_at": now,
                        "key": ks,
                    }
                )
            )
        except OSError as e:
            logger.warning("Cache write failed: %s", e)

    def invalidate(self, task_id: Optional[str] = None) -> int:
        """Remove entries.  If task_id given, only that task; else all."""
        count = 0
        with self._lock:
            if task_id is None:
                count = len(self._memory)
                self._memory.clear()
            else:
                to_remove = [k for k in self._memory if k.startswith(f"{task_id}:")]
                for k in to_remove:
                    del self._memory[k]
                    count += 1

        # Disk cleanup
        if self.cache_dir.exists():
            for f in self.cache_dir.rglob("*.json"):
                if task_id is None or f.stem.startswith(task_id.replace("/", "_")):
                    f.unlink(missing_ok=True)
                    count += 1
        return count

    @property
    def stats(self) -> Dict[str, int]:
        with self._lock:
            return dict(self._stats)

    # ── Internal ────────────────────────────────────────────────────

    def _disk_path(self, key_str: str) -> Path:
        safe = key_str.replace(":", "_").replace("/", "_")
        return self.cache_dir / f"{safe}.json"

    def _promote_to_memory(self, ks: str, result: Dict, created_at: float) -> None:
        with self._lock:
            if len(self._memory) >= self.max_memory_entries:
                self._evict_oldest()
            self._memory[ks] = CacheEntry(result=result, created_at=created_at)

    def _evict_oldest(self) -> None:
        """Remove the least-recently-created entry."""
        if not self._memory:
            return
        oldest_key = min(self._memory, key=lambda k: self._memory[k].created_at)
        del self._memory[oldest_key]
        self._stats["evictions"] += 1


def compute_content_hash(task_dir: Path) -> str:
    """Compute a deterministic hash of task content for cache keying."""
    h = hashlib.sha256()

    instruction = task_dir / "instruction.md"
    if instruction.exists():
        h.update(instruction.read_bytes())

    data_dir = task_dir / "environment" / "data"
    if data_dir.exists():
        for f in sorted(data_dir.rglob("*")):
            if f.is_file():
                h.update(f.name.encode())
                h.update(f.read_bytes())

    setup = task_dir / "environment" / "setup.sh"
    if setup.exists():
        h.update(setup.read_bytes())

    return h.hexdigest()


# Singleton
result_cache = ResultCache()
