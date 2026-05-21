"""FastAPI server for Claw Bench leaderboard.

Provides REST API for submission, leaderboard data, and admin CRUD.

Start with:
    uvicorn claw_bench.server.app:app --host 0.0.0.0 --port 8000 --workers 4
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from claw_bench.server.admin import router as admin_router
from claw_bench.server.submit_api import router as submit_router
from claw_bench.server.task_generator import router as task_gen_router

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
app.include_router(task_gen_router)

# ── Data directory ───────────────────────────────────────────────────

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
_DATA_DIR = _PROJECT_ROOT / "data"
_RESULTS_DIR = _DATA_DIR / "results"
_LEADERBOARD_DIR = _PROJECT_ROOT / "leaderboard" / "out"


# ── Health endpoint ──────────────────────────────────────────────────


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "version": "0.1.0",
        "timestamp": time.time(),
    }


# ── Stats endpoint ────────────────────────────────────────────────────

@app.get("/api/stats")
async def get_stats():
    """Return dynamic task/domain counts from domains.json."""
    config_path = _DATA_DIR / "config" / "domains.json"
    if config_path.exists():
        domains = json.loads(config_path.read_text())
        total_tasks = sum(d.get("tasks", 0) for d in domains)
        return {"totalTasks": total_tasks, "totalDomains": len(domains)}
    return {"totalTasks": 0, "totalDomains": 0}


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


# ── Static file serving (leaderboard frontend) ──────────────────────

if _LEADERBOARD_DIR.exists():
    app.mount(
        "/", StaticFiles(directory=str(_LEADERBOARD_DIR), html=True), name="frontend"
    )

