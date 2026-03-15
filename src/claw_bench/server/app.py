"""FastAPI server for multi-user benchmark execution.

Provides REST API + WebSocket progress streaming for the Claw Bench
leaderboard deployment.  Designed for 200 concurrent users.

Start with:
    uvicorn claw_bench.server.app:app --host 0.0.0.0 --port 8000 --workers 4
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from claw_bench.core.cache import result_cache
from claw_bench.core.rate_limiter import detect_provider, rate_limiters
from claw_bench.core.resource_monitor import UserQuota, monitor
from claw_bench.server.admin import router as admin_router
from claw_bench.server.submit_api import router as submit_router

logger = logging.getLogger(__name__)

# ── App setup ────────────────────────────────────────────────────────

app = FastAPI(
    title="Claw Bench Server",
    description="Multi-user benchmark execution server for AI agents",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_router)
app.include_router(submit_router)

# ── Data directory ───────────────────────────────────────────────────

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
_DATA_DIR = _PROJECT_ROOT / "data"
_RESULTS_DIR = _DATA_DIR / "results"
_LEADERBOARD_DIR = _PROJECT_ROOT / "leaderboard" / "out"


# ── Request/Response models ──────────────────────────────────────────


class RunRequest(BaseModel):
    user_id: str
    framework: str = "openclaw"
    model: str
    tasks: str = "all"
    skills: str = "vanilla"
    tier: Optional[str] = None
    runs: int = 5
    parallel: int = 4
    timeout: int = 300
    claw_id: Optional[str] = None
    mcp_servers: List[str] = []
    memory_modules: List[str] = []


class RunResponse(BaseModel):
    run_id: str
    status: str
    message: str
    estimated_duration_s: Optional[int] = None


class RunStatus(BaseModel):
    run_id: str
    user_id: str
    status: str
    progress: float  # 0-100
    tasks_completed: int
    tasks_total: int
    current_task: Optional[str] = None
    elapsed_s: float = 0
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# ── In-memory run tracking ───────────────────────────────────────────

_active_runs: Dict[str, RunStatus] = {}
_run_lock = asyncio.Lock()

# WebSocket connections per run_id
_ws_connections: Dict[str, List[WebSocket]] = {}


async def _broadcast_progress(run_id: str, status: RunStatus) -> None:
    """Push progress update to all WebSocket clients watching this run."""
    conns = _ws_connections.get(run_id, [])
    data = status.model_dump()
    dead: List[WebSocket] = []
    for ws in conns:
        try:
            await ws.send_json(data)
        except Exception:
            dead.append(ws)
    for ws in dead:
        conns.remove(ws)


# ── Health & system endpoints ────────────────────────────────────────


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "version": "0.1.0",
        "timestamp": time.time(),
    }


@app.get("/api/system/status")
async def system_status():
    """System-wide resource utilisation."""
    return {
        "system": monitor.get_system_status(),
        "cache": result_cache.stats,
        "active_runs": len([r for r in _active_runs.values() if r.status == "running"]),
    }


# ── User endpoints ──────────────────────────────────────────────────


@app.post("/api/users/{user_id}/register")
async def register_user(user_id: str, max_concurrent: int = 8, max_daily: int = 50):
    """Register a user with resource quotas."""
    quota = UserQuota(max_concurrent_tasks=max_concurrent, max_daily_runs=max_daily)
    monitor.register_user(user_id, quota)
    return {
        "user_id": user_id,
        "quota": {"max_concurrent": max_concurrent, "max_daily": max_daily},
    }


@app.get("/api/users/{user_id}/status")
async def user_status(user_id: str):
    status = monitor.get_user_status(user_id)
    if not status:
        raise HTTPException(404, "User not registered")
    return status


# ── Run endpoints ───────────────────────────────────────────────────


@app.post("/api/runs", response_model=RunResponse)
async def create_run(req: RunRequest):
    """Submit a new benchmark run.  Returns immediately with a run_id."""
    # Register user if not already
    monitor.register_user(req.user_id)

    # Check quota
    allowed, reason = monitor.can_start_task(req.user_id)
    if not allowed:
        raise HTTPException(429, reason)

    run_id = str(uuid4())

    # Estimate duration
    task_count = _estimate_task_count(req.tasks, req.tier)
    est_seconds = int(task_count * req.runs * 60 / max(req.parallel, 1))

    status = RunStatus(
        run_id=run_id,
        user_id=req.user_id,
        status="queued",
        progress=0,
        tasks_completed=0,
        tasks_total=task_count * req.runs,
    )

    async with _run_lock:
        _active_runs[run_id] = status

    monitor.run_started(req.user_id)

    # Launch async execution
    asyncio.create_task(_execute_run(run_id, req))

    return RunResponse(
        run_id=run_id,
        status="queued",
        message=f"Run queued: {task_count} tasks × {req.runs} runs",
        estimated_duration_s=est_seconds,
    )


@app.get("/api/runs/{run_id}", response_model=RunStatus)
async def get_run(run_id: str):
    status = _active_runs.get(run_id)
    if not status:
        raise HTTPException(404, "Run not found")
    return status


@app.get("/api/runs/{run_id}/results")
async def get_run_results(run_id: str):
    status = _active_runs.get(run_id)
    if not status:
        raise HTTPException(404, "Run not found")
    if status.status != "completed":
        raise HTTPException(409, f"Run is {status.status}, not completed")
    return status.results


@app.post("/api/runs/{run_id}/cancel")
async def cancel_run(run_id: str):
    status = _active_runs.get(run_id)
    if not status:
        raise HTTPException(404, "Run not found")
    status.status = "cancelled"
    return {"run_id": run_id, "status": "cancelled"}


# ── WebSocket progress stream ──────────────────────────────────────


@app.websocket("/ws/runs/{run_id}")
async def ws_run_progress(ws: WebSocket, run_id: str):
    """Stream real-time progress updates for a run."""
    await ws.accept()

    if run_id not in _ws_connections:
        _ws_connections[run_id] = []
    _ws_connections[run_id].append(ws)

    # Send current state immediately
    status = _active_runs.get(run_id)
    if status:
        await ws.send_json(status.model_dump())

    try:
        while True:
            # Keep connection alive; client can send ping/pong
            await ws.receive_text()
    except WebSocketDisconnect:
        _ws_connections.get(run_id, []).remove(ws) if ws in _ws_connections.get(
            run_id, []
        ) else None


# ── Public config endpoint ────────────────────────────────────────────

@app.get("/api/config/{name}")
async def get_public_config(name: str):
    """Public read-only access to config files (domains, models, capabilities)."""
    if name not in ("domains", "models", "capabilities"):
        raise HTTPException(404, "Config not found")
    config_path = _DATA_DIR / "config" / f"{name}.json"
    if not config_path.exists():
        raise HTTPException(404, "Config not found")
    return json.loads(config_path.read_text())


# ── Leaderboard data endpoints ──────────────────────────────────────


@app.get("/api/leaderboard")
async def get_leaderboard():
    """Return all benchmark results for the leaderboard."""
    results = []
    if _RESULTS_DIR.exists():
        for f in sorted(_RESULTS_DIR.glob("*.json")):
            try:
                data = json.loads(f.read_text())
                if isinstance(data, list):
                    results.extend(data)
                else:
                    results.append(data)
            except (json.JSONDecodeError, OSError):
                continue
    return results


@app.get("/api/leaderboard/{framework}/{model}")
async def get_result(framework: str, model: str):
    """Get specific framework/model result."""
    safe_name = f"{framework}-{model}".replace("/", "-")
    result_file = _RESULTS_DIR / f"{safe_name}.json"
    if not result_file.exists():
        raise HTTPException(404, f"No results for {framework}/{model}")
    return json.loads(result_file.read_text())


@app.get("/api/cache/stats")
async def cache_stats():
    return result_cache.stats


@app.post("/api/cache/invalidate")
async def invalidate_cache(task_id: Optional[str] = None):
    count = result_cache.invalidate(task_id)
    return {"invalidated": count}


# ── Static file serving (leaderboard frontend) ──────────────────────

if _LEADERBOARD_DIR.exists():
    app.mount(
        "/", StaticFiles(directory=str(_LEADERBOARD_DIR), html=True), name="frontend"
    )


# ── Run execution engine ────────────────────────────────────────────


async def _execute_run(run_id: str, req: RunRequest) -> None:
    """Execute a benchmark run asynchronously with progress tracking."""
    from claw_bench.adapters.registry import get_adapter
    from claw_bench.core.agent_profile import AgentProfile
    from claw_bench.core.cache import CacheKey, compute_content_hash
    from claw_bench.core.runner import RunConfig, run_single_task, save_results
    from claw_bench.core.task_loader import load_all_tasks

    status = _active_runs[run_id]
    status.status = "running"
    start_time = time.time()

    try:
        # Find tasks root
        tasks_root = _PROJECT_ROOT / "tasks"
        if not tasks_root.is_dir():
            raise FileNotFoundError("tasks/ directory not found")

        # Load tasks
        task_list, task_dirs = load_all_tasks(tasks_root)

        # Apply tier filtering
        if req.tier == "quick":
            from claw_bench.core.test_tiers import select_quick_tasks

            task_list = select_quick_tasks(task_list)
            task_dirs = {t.id: task_dirs[t.id] for t in task_list if t.id in task_dirs}
            req.runs = 1

        status.tasks_total = len(task_list) * req.runs
        await _broadcast_progress(run_id, status)

        # Initialize adapter
        adapter = get_adapter(req.framework)
        adapter_config: dict = {"model": req.model, "timeout": req.timeout}
        if os.environ.get("OPENAI_COMPAT_BASE_URL"):
            adapter_config["base_url"] = os.environ["OPENAI_COMPAT_BASE_URL"]
        if os.environ.get("OPENAI_COMPAT_API_KEY"):
            adapter_config["api_key"] = os.environ["OPENAI_COMPAT_API_KEY"]
        adapter.setup(adapter_config)

        # Execute tasks with bounded concurrency
        sem = asyncio.Semaphore(req.parallel)
        results = []
        loop = asyncio.get_event_loop()

        async def _run_one(task, run_idx):
            task_dir = task_dirs[task.id]

            # Check cache
            content_hash = compute_content_hash(task_dir)
            cache_key = CacheKey(task.id, req.model, req.skills, content_hash)
            cached = result_cache.get(cache_key)

            if cached and "score" in cached:
                from claw_bench.core.runner import TaskResult

                return TaskResult(
                    task_id=cached["task_id"],
                    passed=cached["passed"],
                    score=cached["score"],
                    duration_s=cached["duration_s"],
                    tokens_input=cached.get("tokens_input", 0),
                    tokens_output=cached.get("tokens_output", 0),
                    skills_mode=req.skills,
                )

            # Rate limit
            bucket = rate_limiters.get(
                detect_provider(os.environ.get("OPENAI_COMPAT_BASE_URL", ""))
            )
            await bucket.async_acquire()

            monitor.task_started(req.user_id)
            try:
                result = await loop.run_in_executor(
                    None,
                    lambda: run_single_task(
                        task, task_dir, adapter, req.timeout, req.skills
                    ),
                )
                # Cache result
                result_cache.put(
                    cache_key,
                    {
                        "task_id": result.task_id,
                        "passed": result.passed,
                        "score": result.score,
                        "duration_s": result.duration_s,
                        "tokens_input": result.tokens_input,
                        "tokens_output": result.tokens_output,
                    },
                )
                return result
            finally:
                monitor.task_completed(req.user_id)

        async def _run_with_sem(task, run_idx):
            async with sem:
                if status.status == "cancelled":
                    return None
                status.current_task = task.id
                result = await _run_one(task, run_idx)
                if result:
                    results.append(result)
                    status.tasks_completed += 1
                    status.progress = round(
                        status.tasks_completed / max(status.tasks_total, 1) * 100, 1
                    )
                    status.elapsed_s = round(time.time() - start_time, 1)
                    await _broadcast_progress(run_id, status)
                return result

        # Create all task coroutines
        coros = []
        for task in task_list:
            for run_idx in range(req.runs):
                coros.append(_run_with_sem(task, run_idx))

        await asyncio.gather(*coros, return_exceptions=True)

        if status.status == "cancelled":
            return

        # Save results
        user_output = _PROJECT_ROOT / "results" / req.user_id / run_id
        profile = AgentProfile(
            model=req.model,
            framework=req.framework,
            skills_mode=req.skills,
            mcp_servers=req.mcp_servers,
            memory_modules=req.memory_modules,
        )
        config = RunConfig(
            framework=req.framework,
            model=req.model,
            tasks_root=tasks_root,
            output_dir=user_output,
            runs=req.runs,
            parallel=req.parallel,
            timeout=req.timeout,
            skills=req.skills,
            agent_profile=profile,
            test_tier=req.tier,
        )
        save_results(results, config, user_output, tasks=task_list)

        adapter.teardown()

        # Update status
        total = len(results)
        passed = sum(1 for r in results if r.passed)
        overall = sum(r.score for r in results) / max(total, 1) * 100

        status.status = "completed"
        status.progress = 100
        status.elapsed_s = round(time.time() - start_time, 1)
        status.results = {
            "total": total,
            "passed": passed,
            "overall": round(overall, 1),
            "pass_rate": round(passed / max(total, 1) * 100, 1),
            "output_dir": str(user_output),
        }
        await _broadcast_progress(run_id, status)

    except Exception as e:
        status.status = "failed"
        status.error = str(e)
        status.elapsed_s = round(time.time() - start_time, 1)
        logger.exception("Run %s failed", run_id)
        await _broadcast_progress(run_id, status)


def _estimate_task_count(tasks_filter: str, tier: Optional[str]) -> int:
    """Rough estimate of task count for duration prediction."""
    if tier == "quick":
        return 14
    if tier == "comprehensive":
        return 210
    if tasks_filter == "all":
        return 210
    if tasks_filter.upper() in ("L1", "L2", "L3", "L4"):
        return 50
    return 15  # domain default
