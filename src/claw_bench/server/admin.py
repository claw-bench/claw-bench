"""Admin API for managing benchmark data.

Provides CRUD endpoints for leaderboard results, skills-gain data,
and MoltBook agents. Protected by a simple token.
"""

from __future__ import annotations

import json
import hashlib
import os
import secrets
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel

router = APIRouter(prefix="/api/admin", tags=["admin"])

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
_DATA_DIR = _PROJECT_ROOT / "data"
_RESULTS_DIR = _DATA_DIR / "results"
_SKILLS_DIR = _DATA_DIR / "skills-gain"
_MOLTBOOK_DIR = _DATA_DIR / "moltbook"
_ADMIN_FILE = _DATA_DIR / ".admin_token"

for d in [_RESULTS_DIR, _SKILLS_DIR, _MOLTBOOK_DIR]:
    try:
        d.mkdir(parents=True, exist_ok=True)
    except OSError:
        pass


def _get_or_create_token() -> str:
    if _ADMIN_FILE.exists():
        return _ADMIN_FILE.read_text().strip()
    token = secrets.token_urlsafe(32)
    _ADMIN_FILE.write_text(token)
    import logging
    logging.getLogger(__name__).warning("Admin token created: %s", token)
    return token


def verify_admin(authorization: str = Header(...)) -> str:
    token = authorization.replace("Bearer ", "")
    if not secrets.compare_digest(token, _get_or_create_token()):
        raise HTTPException(401, "Invalid admin token")
    return token


# ── Auth ─────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    password: str


@router.post("/login")
async def admin_login(req: LoginRequest):
    expected = os.environ.get("ADMIN_PASSWORD", "")
    if not expected:
        raise HTTPException(503, "Admin password not configured. Set ADMIN_PASSWORD environment variable.")
    if not secrets.compare_digest(req.password, expected):
        raise HTTPException(401, "Invalid password")
    return {"token": _get_or_create_token()}


# ── Result CRUD ──────────────────────────────────────────────────────

class AgentProfileInput(BaseModel):
    profileId: Optional[str] = None
    displayName: str
    model: str
    framework: str
    skillsMode: str = "vanilla"
    skills: List[str] = []
    mcpServers: List[str] = []
    memoryModules: List[str] = []
    modelTier: Optional[str] = None
    tags: Dict[str, str] = {}


class ProgressiveInput(BaseModel):
    baseline_pass_rate: float = 0
    current_pass_rate: float = 0
    absolute_gain: float = 0
    normalized_gain: float = 0


class ResultInput(BaseModel):
    framework: str
    model: str
    overall: float
    taskCompletion: float
    efficiency: float
    security: float
    skills: float
    ux: float
    testTier: Optional[str] = "comprehensive"
    agentProfile: Optional[AgentProfileInput] = None
    progressive: Optional[ProgressiveInput] = None


def _result_filename(r: dict) -> str:
    profile_id = ""
    if r.get("agentProfile") and r["agentProfile"].get("profileId"):
        profile_id = f"-{r['agentProfile']['profileId']}"
    name = f"{r['framework']}-{r['model']}{profile_id}".replace("/", "-").replace(" ", "_")
    return f"{name}.json"


@router.get("/results")
async def list_results(_: str = Depends(verify_admin)):
    results = []
    for f in sorted(_RESULTS_DIR.glob("*.json")):
        try:
            data = json.loads(f.read_text())
            entry = data if isinstance(data, dict) else data[0] if data else {}
            entry["_filename"] = f.name
            results.append(entry)
        except (json.JSONDecodeError, OSError, IndexError):
            continue
    return results


@router.post("/results")
async def create_result(req: ResultInput, _: str = Depends(verify_admin)):
    data = req.model_dump()
    if data.get("agentProfile") and not data["agentProfile"].get("profileId"):
        data["agentProfile"]["profileId"] = uuid4().hex[:6]
    filename = _result_filename(data)
    filepath = _RESULTS_DIR / filename
    filepath.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    return {"status": "created", "filename": filename, "data": data}


@router.put("/results/{filename}")
async def update_result(filename: str, req: ResultInput, _: str = Depends(verify_admin)):
    filepath = _RESULTS_DIR / filename
    if not filepath.exists():
        raise HTTPException(404, f"Result file {filename} not found")
    data = req.model_dump()
    if data.get("agentProfile") and not data["agentProfile"].get("profileId"):
        data["agentProfile"]["profileId"] = uuid4().hex[:6]
    filepath.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    return {"status": "updated", "filename": filename, "data": data}


@router.delete("/results/{filename}")
async def delete_result(filename: str, _: str = Depends(verify_admin)):
    filepath = _RESULTS_DIR / filename
    if not filepath.exists():
        raise HTTPException(404, f"Result file {filename} not found")
    filepath.unlink()
    return {"status": "deleted", "filename": filename}


# ── Skills Gain CRUD ─────────────────────────────────────────────────

class SkillsGainInput(BaseModel):
    framework: str
    model: str
    vanilla: float
    curated: float
    native: float


@router.get("/skills-gain")
async def list_skills_gain(_: str = Depends(verify_admin)):
    filepath = _SKILLS_DIR / "skills-gain.json"
    if not filepath.exists():
        return []
    try:
        return json.loads(filepath.read_text())
    except (json.JSONDecodeError, OSError):
        return []


@router.post("/skills-gain")
async def save_skills_gain(entries: List[SkillsGainInput], _: str = Depends(verify_admin)):
    filepath = _SKILLS_DIR / "skills-gain.json"
    data = [e.model_dump() for e in entries]
    filepath.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    return {"status": "saved", "count": len(data)}


# ── MoltBook Agent CRUD ──────────────────────────────────────────────

class MoltBookAgentInput(BaseModel):
    clawId: str
    displayName: str
    framework: str
    model: str
    submitter: Optional[str] = None
    modelTier: Optional[str] = None
    runs: List[Dict[str, Any]] = []


@router.get("/moltbook")
async def list_moltbook_agents(_: str = Depends(verify_admin)):
    agents = []
    for f in sorted(_MOLTBOOK_DIR.glob("*.json")):
        try:
            agents.append(json.loads(f.read_text()))
        except (json.JSONDecodeError, OSError):
            continue
    return agents


@router.post("/moltbook")
async def create_moltbook_agent(req: MoltBookAgentInput, _: str = Depends(verify_admin)):
    data = req.model_dump()
    filepath = _MOLTBOOK_DIR / f"{req.clawId}.json"
    filepath.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    return {"status": "created", "clawId": req.clawId}


@router.put("/moltbook/{claw_id}")
async def update_moltbook_agent(claw_id: str, req: MoltBookAgentInput, _: str = Depends(verify_admin)):
    filepath = _MOLTBOOK_DIR / f"{claw_id}.json"
    if not filepath.exists():
        raise HTTPException(404, f"Agent {claw_id} not found")
    data = req.model_dump()
    filepath.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    return {"status": "updated", "clawId": claw_id}


@router.delete("/moltbook/{claw_id}")
async def delete_moltbook_agent(claw_id: str, _: str = Depends(verify_admin)):
    filepath = _MOLTBOOK_DIR / f"{claw_id}.json"
    if not filepath.exists():
        raise HTTPException(404, f"Agent {claw_id} not found")
    filepath.unlink()
    return {"status": "deleted", "clawId": claw_id}


# ── Pending Submissions (approval workflow) ──────────────────────────

_PENDING_DIR = _DATA_DIR / "pending"
try:
    _PENDING_DIR.mkdir(parents=True, exist_ok=True)
except OSError:
    pass


@router.get("/pending")
async def list_pending(_: str = Depends(verify_admin)):
    items = []
    for f in sorted(_PENDING_DIR.glob("*.json")):
        try:
            data = json.loads(f.read_text())
            data["_filename"] = f.name
            items.append(data)
        except (json.JSONDecodeError, OSError):
            continue
    return items


@router.post("/pending/{filename}/approve")
async def approve_submission(filename: str, _: str = Depends(verify_admin)):
    pending_path = _PENDING_DIR / filename
    if not pending_path.exists():
        raise HTTPException(404, "Pending submission not found")

    data = json.loads(pending_path.read_text())

    for key in ("_submittedBy", "_submittedAt", "_status", "_previousScore", "_existingFile", "_filename"):
        data.pop(key, None)

    existing_file = None
    claw_id = data.get("clawId", "")
    if claw_id:
        for f in _RESULTS_DIR.glob("*.json"):
            try:
                existing = json.loads(f.read_text())
                if existing.get("clawId") == claw_id:
                    existing_file = f
                    break
            except (json.JSONDecodeError, OSError):
                continue

    if existing_file:
        existing_data = json.loads(existing_file.read_text())
        if data.get("overall", 0) > existing_data.get("overall", 0):
            existing_file.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            existing_data["submissionCount"] = data.get("submissionCount", existing_data.get("submissionCount", 1))
            existing_data["lastUpdated"] = data.get("lastUpdated", existing_data.get("lastUpdated"))
            existing_data["region"] = data.get("region", existing_data.get("region"))
            existing_file.write_text(json.dumps(existing_data, indent=2, ensure_ascii=False))
        result_filename = existing_file.name
    else:
        profile_id = data.get("clawId") or data.get("agentProfile", {}).get("profileId", "")
        safe_name = f"{data.get('framework','')}-{data.get('model','')}-{profile_id}".replace("/", "-").replace(" ", "_")
        result_filename = f"{safe_name}.json"
        (_RESULTS_DIR / result_filename).write_text(json.dumps(data, indent=2, ensure_ascii=False))

    pending_path.unlink()
    return {"status": "approved", "filename": result_filename}


@router.post("/pending/{filename}/reject")
async def reject_submission(filename: str, _: str = Depends(verify_admin)):
    pending_path = _PENDING_DIR / filename
    if not pending_path.exists():
        raise HTTPException(404, "Pending submission not found")
    pending_path.unlink()
    return {"status": "rejected", "filename": filename}


# ── Config CRUD (domains, models, capabilities) ─────────────────────

_CONFIG_DIR = _DATA_DIR / "config"
try:
    _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
except OSError:
    pass


@router.get("/config/{name}")
async def get_config(name: str, _: str = Depends(verify_admin)):
    filepath = _CONFIG_DIR / f"{name}.json"
    if not filepath.exists():
        raise HTTPException(404, f"Config '{name}' not found")
    return json.loads(filepath.read_text())


@router.put("/config/{name}")
async def update_config(name: str, data: dict, _: str = Depends(verify_admin)):
    if name not in ("domains", "models", "capabilities"):
        raise HTTPException(400, f"Unknown config: {name}")
    filepath = _CONFIG_DIR / f"{name}.json"
    filepath.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    return {"status": "updated", "config": name}


# ── Rebuild trigger ──────────────────────────────────────────────────

@router.post("/rebuild")
async def trigger_rebuild(_: str = Depends(verify_admin)):
    """Trigger a frontend rebuild to reflect data changes."""
    import subprocess
    leaderboard_dir = _PROJECT_ROOT / "leaderboard"
    try:
        result = subprocess.run(
            ["npm", "run", "build"],
            cwd=str(leaderboard_dir),
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            return {"status": "error", "stderr": result.stderr[-500:]}
        return {"status": "rebuilt", "message": "Frontend rebuilt successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
