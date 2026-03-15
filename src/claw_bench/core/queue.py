"""Async task queue with concurrency control for multi-user deployments.

Replaces the bare ThreadPoolExecutor with a bounded-concurrency queue that
integrates rate limiting, result caching, and per-user quotas.
"""

from __future__ import annotations

import asyncio
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from uuid import uuid4

from claw_bench.core.cache import CacheKey, compute_content_hash, result_cache
from claw_bench.core.rate_limiter import detect_provider, rate_limiters
from claw_bench.core.resource_monitor import monitor

logger = logging.getLogger(__name__)


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Job:
    """Represents a single task execution in the queue."""

    job_id: str
    user_id: str
    task_id: str
    model: str
    skills_mode: str
    status: JobStatus = JobStatus.QUEUED
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: float = 0.0
    started_at: float = 0.0
    completed_at: float = 0.0
    cached: bool = False

    def __post_init__(self) -> None:
        if not self.created_at:
            self.created_at = time.time()


class TaskQueue:
    """Bounded async task queue with per-user fairness.

    Key design decisions for 200-user deployment:
    - Global semaphore limits total concurrent tasks (default 200)
    - Per-user semaphore limits individual user's concurrency (default 8)
    - ThreadPoolExecutor runs blocking adapter calls off the event loop
    - Rate limiter gates API calls per provider
    - Result cache avoids redundant LLM calls
    """

    def __init__(
        self,
        max_global_concurrency: int = 200,
        max_user_concurrency: int = 8,
        thread_pool_size: int = 100,
        api_base_url: str = "",
    ) -> None:
        self.max_global = max_global_concurrency
        self.max_user = max_user_concurrency

        self._global_sem = asyncio.Semaphore(max_global_concurrency)
        self._user_sems: Dict[str, asyncio.Semaphore] = {}
        self._pool = ThreadPoolExecutor(max_workers=thread_pool_size)

        self._jobs: Dict[str, Job] = {}
        self._provider = detect_provider(api_base_url) if api_base_url else "default"
        self._lock = asyncio.Lock()

        # Metrics
        self._total_submitted = 0
        self._total_completed = 0
        self._total_cached = 0

    def _get_user_sem(self, user_id: str) -> asyncio.Semaphore:
        if user_id not in self._user_sems:
            self._user_sems[user_id] = asyncio.Semaphore(self.max_user)
        return self._user_sems[user_id]

    async def submit(
        self,
        user_id: str,
        task_id: str,
        task_dir: Path,
        model: str,
        skills_mode: str,
        execute_fn: Callable[..., Dict[str, Any]],
        **kwargs: Any,
    ) -> Job:
        """Submit a task for execution.  Returns immediately with a Job handle."""
        # Check quota
        allowed, reason = monitor.can_start_task(user_id)
        if not allowed:
            job = Job(
                job_id=str(uuid4()),
                user_id=user_id,
                task_id=task_id,
                model=model,
                skills_mode=skills_mode,
                status=JobStatus.FAILED,
                error=f"Rejected: {reason}",
            )
            self._jobs[job.job_id] = job
            return job

        job = Job(
            job_id=str(uuid4()),
            user_id=user_id,
            task_id=task_id,
            model=model,
            skills_mode=skills_mode,
        )
        async with self._lock:
            self._jobs[job.job_id] = job
            self._total_submitted += 1

        # Check cache first
        content_hash = compute_content_hash(task_dir)
        cache_key = CacheKey(
            task_id=task_id,
            model=model,
            skills_mode=skills_mode,
            content_hash=content_hash,
        )
        cached_result = result_cache.get(cache_key)
        if cached_result is not None:
            job.result = cached_result
            job.status = JobStatus.COMPLETED
            job.completed_at = time.time()
            job.cached = True
            async with self._lock:
                self._total_completed += 1
                self._total_cached += 1
            logger.info("Cache hit for %s/%s", task_id, model)
            return job

        # Schedule execution
        asyncio.create_task(self._execute(job, cache_key, execute_fn, **kwargs))
        return job

    async def _execute(
        self,
        job: Job,
        cache_key: CacheKey,
        execute_fn: Callable[..., Dict[str, Any]],
        **kwargs: Any,
    ) -> None:
        """Execute a job with concurrency control and rate limiting."""
        user_sem = self._get_user_sem(job.user_id)

        try:
            # Acquire both global and per-user semaphores
            async with self._global_sem:
                async with user_sem:
                    job.status = JobStatus.RUNNING
                    job.started_at = time.time()
                    monitor.task_started(job.user_id)

                    # Rate limit
                    bucket = rate_limiters.get(self._provider)
                    await bucket.async_acquire()

                    # Run blocking adapter call in thread pool
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(
                        self._pool, execute_fn, **kwargs
                    )

                    job.result = result
                    job.status = JobStatus.COMPLETED
                    job.completed_at = time.time()

                    # Cache the result
                    result_cache.put(cache_key, result)

                    tokens = result.get("tokens_input", 0) + result.get(
                        "tokens_output", 0
                    )
                    monitor.task_completed(job.user_id, tokens)

                    async with self._lock:
                        self._total_completed += 1

        except Exception as e:
            job.status = JobStatus.FAILED
            job.error = str(e)
            job.completed_at = time.time()
            monitor.task_completed(job.user_id)
            logger.error("Job %s failed: %s", job.job_id, e)

    def get_job(self, job_id: str) -> Optional[Job]:
        return self._jobs.get(job_id)

    def get_user_jobs(self, user_id: str) -> List[Job]:
        return [j for j in self._jobs.values() if j.user_id == user_id]

    @property
    def stats(self) -> Dict[str, Any]:
        active = sum(1 for j in self._jobs.values() if j.status == JobStatus.RUNNING)
        queued = sum(1 for j in self._jobs.values() if j.status == JobStatus.QUEUED)
        return {
            "total_submitted": self._total_submitted,
            "total_completed": self._total_completed,
            "total_cached": self._total_cached,
            "active_jobs": active,
            "queued_jobs": queued,
            "cache_hit_rate": (
                round(self._total_cached / max(self._total_completed, 1) * 100, 1)
            ),
        }

    async def shutdown(self) -> None:
        """Graceful shutdown — wait for running tasks to complete."""
        self._pool.shutdown(wait=True)
