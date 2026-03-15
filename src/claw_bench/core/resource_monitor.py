"""Lightweight resource monitor for multi-user benchmark deployments.

Tracks system-wide and per-user resource usage so the server can enforce
limits and report utilisation to operators.
"""

from __future__ import annotations

import os
import threading
import time
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class UserQuota:
    """Per-user resource limits."""

    max_concurrent_tasks: int = 8
    max_parallel_workers: int = 4
    max_daily_runs: int = 50
    max_tasks_per_run: int = 210


@dataclass
class UserUsage:
    """Live usage counters for a single user."""

    active_tasks: int = 0
    total_runs_today: int = 0
    total_tasks_today: int = 0
    total_tokens_today: int = 0
    last_activity: float = field(default_factory=time.time)


class ResourceMonitor:
    """Thread-safe resource monitor with per-user tracking."""

    def __init__(self, default_quota: Optional[UserQuota] = None) -> None:
        self.default_quota = default_quota or UserQuota()
        self._users: Dict[str, UserUsage] = {}
        self._quotas: Dict[str, UserQuota] = {}
        self._lock = threading.Lock()

        # Global counters
        self._global_active_tasks = 0
        self._global_max_tasks = 800  # 200 users × 4 parallel
        self._global_active_users = 0

    # ── User management ─────────────────────────────────────────────

    def register_user(self, user_id: str, quota: Optional[UserQuota] = None) -> None:
        with self._lock:
            if user_id not in self._users:
                self._users[user_id] = UserUsage()
                self._global_active_users += 1
            if quota:
                self._quotas[user_id] = quota

    def get_quota(self, user_id: str) -> UserQuota:
        return self._quotas.get(user_id, self.default_quota)

    # ── Task lifecycle ──────────────────────────────────────────────

    def can_start_task(self, user_id: str) -> tuple[bool, str]:
        """Check if user can start a new task.  Returns (allowed, reason)."""
        with self._lock:
            if self._global_active_tasks >= self._global_max_tasks:
                return (
                    False,
                    f"System at capacity ({self._global_active_tasks}/{self._global_max_tasks} tasks)",
                )

            usage = self._users.get(user_id)
            if usage is None:
                return False, "User not registered"

            quota = self.get_quota(user_id)
            if usage.active_tasks >= quota.max_concurrent_tasks:
                return (
                    False,
                    f"User task limit reached ({usage.active_tasks}/{quota.max_concurrent_tasks})",
                )

            if usage.total_runs_today >= quota.max_daily_runs:
                return (
                    False,
                    f"Daily run limit reached ({usage.total_runs_today}/{quota.max_daily_runs})",
                )

            return True, "ok"

    def task_started(self, user_id: str) -> None:
        with self._lock:
            usage = self._users.setdefault(user_id, UserUsage())
            usage.active_tasks += 1
            usage.total_tasks_today += 1
            usage.last_activity = time.time()
            self._global_active_tasks += 1

    def task_completed(self, user_id: str, tokens_used: int = 0) -> None:
        with self._lock:
            usage = self._users.get(user_id)
            if usage:
                usage.active_tasks = max(0, usage.active_tasks - 1)
                usage.total_tokens_today += tokens_used
                usage.last_activity = time.time()
            self._global_active_tasks = max(0, self._global_active_tasks - 1)

    def run_started(self, user_id: str) -> None:
        with self._lock:
            usage = self._users.setdefault(user_id, UserUsage())
            usage.total_runs_today += 1

    # ── Reporting ───────────────────────────────────────────────────

    def get_system_status(self) -> Dict:
        with self._lock:
            return {
                "active_tasks": self._global_active_tasks,
                "max_tasks": self._global_max_tasks,
                "utilization": round(
                    self._global_active_tasks / max(self._global_max_tasks, 1) * 100, 1
                ),
                "active_users": sum(
                    1 for u in self._users.values() if u.active_tasks > 0
                ),
                "registered_users": len(self._users),
                "system_memory_mb": _get_process_memory_mb(),
                "cpu_count": os.cpu_count() or 1,
            }

    def get_user_status(self, user_id: str) -> Optional[Dict]:
        with self._lock:
            usage = self._users.get(user_id)
            if not usage:
                return None
            quota = self.get_quota(user_id)
            return {
                "active_tasks": usage.active_tasks,
                "max_concurrent_tasks": quota.max_concurrent_tasks,
                "total_runs_today": usage.total_runs_today,
                "max_daily_runs": quota.max_daily_runs,
                "total_tokens_today": usage.total_tokens_today,
                "last_activity": usage.last_activity,
            }

    def reset_daily_counters(self) -> None:
        """Call at midnight to reset daily limits."""
        with self._lock:
            for usage in self._users.values():
                usage.total_runs_today = 0
                usage.total_tasks_today = 0
                usage.total_tokens_today = 0


def _get_process_memory_mb() -> float:
    """Get current process RSS in MB."""
    try:
        import resource

        # getrusage returns KB on Linux, bytes on macOS
        rusage = resource.getrusage(resource.RUSAGE_SELF)
        rss = rusage.ru_maxrss
        if os.uname().sysname == "Darwin":
            return round(rss / 1024 / 1024, 1)  # bytes -> MB
        return round(rss / 1024, 1)  # KB -> MB
    except Exception:
        return 0.0


# Singleton
monitor = ResourceMonitor()
