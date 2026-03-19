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

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Header
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

# ── Expert Contribution System ─────────────────────────────────────────────

_PROPOSALS_DIR = _DATA_DIR / "expert-proposals"
_EXPERTS_DIR = _DATA_DIR / "experts"
_INVITES_FILE = _DATA_DIR / "invite_codes.json"

for _d in [_PROPOSALS_DIR, _EXPERTS_DIR]:
    try:
        _d.mkdir(parents=True, exist_ok=True)
    except OSError:
        pass


# ── Expert Account System ────────────────────────────────────────────

def _load_experts() -> Dict[str, Dict]:
    """Load all expert accounts from disk."""
    experts = {}
    for f in _EXPERTS_DIR.glob("*.json"):
        try:
            data = json.loads(f.read_text())
            experts[data["username"]] = data
        except (json.JSONDecodeError, KeyError, OSError):
            continue
    return experts


def _save_expert(data: Dict):
    filepath = _EXPERTS_DIR / f"{data['username']}.json"
    filepath.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def _load_invites() -> List[Dict]:
    if _INVITES_FILE.exists():
        try:
            return json.loads(_INVITES_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return []


def _save_invites(invites: List[Dict]):
    _INVITES_FILE.write_text(json.dumps(invites, indent=2, ensure_ascii=False))


def _hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    h = hashlib.sha256(f"{salt}:{password}".encode()).hexdigest()
    return f"{salt}:{h}"


def _check_password(stored: str, password: str) -> bool:
    salt, h = stored.split(":", 1)
    return secrets.compare_digest(h, hashlib.sha256(f"{salt}:{password}".encode()).hexdigest())


def _create_expert_token(username: str) -> str:
    payload = f"{username}:{secrets.token_urlsafe(24)}"
    return payload


def verify_expert(authorization: str = Header(...)) -> str:
    """Verify expert token and return the username."""
    token = authorization.replace("Bearer ", "")
    if ":" not in token:
        raise HTTPException(401, "Invalid token format")
    username = token.split(":", 1)[0]
    expert_file = _EXPERTS_DIR / f"{username}.json"
    if not expert_file.exists():
        raise HTTPException(401, "Expert account not found")
    data = json.loads(expert_file.read_text())
    if data.get("status") != "active":
        raise HTTPException(403, "Account is disabled")
    if data.get("token") != token:
        raise HTTPException(401, "Invalid or expired token")
    return username



def _verify_proposal_owner(proposal_id: str, username: str):
    """Ensure the proposal belongs to the requesting expert."""
    filepath = _PROPOSALS_DIR / f"{proposal_id}.json"
    if not filepath.exists():
        raise HTTPException(404, 'Proposal not found')
    data = json.loads(filepath.read_text())
    owner = data.get('_submittedBy', '')
    if owner and owner != username:
        raise HTTPException(403, 'You can only access your own proposals')
    return data

class ExpertRegisterInput(BaseModel):
    username: str
    password: str
    displayName: str
    email: str = ""
    organization: str = ""
    inviteCode: str


class ExpertLoginInput(BaseModel):
    username: str
    password: str


@router.post("/expert-register")
async def expert_register(req: ExpertRegisterInput):
    """Register a new expert account with an invite code."""
    if len(req.username) < 3 or len(req.username) > 30:
        raise HTTPException(422, "Username must be 3-30 characters")
    if not req.username.isalnum() and not all(c.isalnum() or c in "-_" for c in req.username):
        raise HTTPException(422, "Username can only contain letters, numbers, hyphens, underscores")
    if len(req.password) < 6:
        raise HTTPException(422, "Password must be at least 6 characters")

    expert_file = _EXPERTS_DIR / f"{req.username}.json"
    if expert_file.exists():
        raise HTTPException(409, "Username already taken")

    invites = _load_invites()
    invite = None
    for inv in invites:
        if inv["code"] == req.inviteCode and not inv.get("used"):
            invite = inv
            break

    if not invite:
        raise HTTPException(403, "Invalid or already used invite code")

    invite["used"] = True
    invite["usedBy"] = req.username
    invite["usedAt"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    _save_invites(invites)

    token = _create_expert_token(req.username)
    expert_data = {
        "username": req.username,
        "passwordHash": _hash_password(req.password),
        "displayName": req.displayName,
        "email": req.email,
        "organization": req.organization,
        "token": token,
        "status": "active",
        "role": "expert",
        "invitedBy": invite.get("createdBy", "system"),
        "registeredAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "proposalCount": 0,
        "inviteCodesGenerated": 0,
    }
    _save_expert(expert_data)

    return {"status": "registered", "username": req.username, "token": token}


@router.post("/expert-login")
async def expert_login(req: ExpertLoginInput):
    """Login as an expert and get a session token."""
    expert_file = _EXPERTS_DIR / f"{req.username}.json"
    if not expert_file.exists():
        raise HTTPException(401, "Invalid username or password")

    data = json.loads(expert_file.read_text())
    if not _check_password(data["passwordHash"], req.password):
        raise HTTPException(401, "Invalid username or password")

    if data.get("status") != "active":
        raise HTTPException(403, "Account is disabled")

    token = _create_expert_token(req.username)
    data["token"] = token
    _save_expert(data)

    return {"token": token, "username": req.username, "displayName": data.get("displayName", "")}


@router.get("/expert-profile")
async def expert_profile(username: str = Depends(verify_expert)):
    """Get current expert's profile."""
    data = json.loads((_EXPERTS_DIR / f"{username}.json").read_text())
    return {
        "username": data["username"],
        "displayName": data.get("displayName", ""),
        "email": data.get("email", ""),
        "organization": data.get("organization", ""),
        "role": data.get("role", "expert"),
        "proposalCount": data.get("proposalCount", 0),
        "inviteCodesGenerated": data.get("inviteCodesGenerated", 0),
        "registeredAt": data.get("registeredAt", ""),
    }


@router.post("/expert-invite-codes")
async def generate_invite_codes(username: str = Depends(verify_expert)):
    """Generate a new invite code (each expert can create multiple)."""
    code = secrets.token_urlsafe(12)
    invites = _load_invites()
    invites.append({
        "code": code,
        "createdBy": username,
        "createdAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "used": False,
        "usedBy": None,
        "usedAt": None,
    })
    _save_invites(invites)

    expert_data = json.loads((_EXPERTS_DIR / f"{username}.json").read_text())
    expert_data["inviteCodesGenerated"] = expert_data.get("inviteCodesGenerated", 0) + 1
    _save_expert(expert_data)

    return {"code": code}


@router.get("/expert-invite-codes")
async def list_my_invite_codes(username: str = Depends(verify_expert)):
    """List invite codes created by the current expert."""
    invites = _load_invites()
    my_codes = [inv for inv in invites if inv.get("createdBy") == username]
    return my_codes


# ── Admin: Expert Account Management ─────────────────────────────────

@router.get("/experts")
async def list_experts(_: str = Depends(verify_admin)):
    """List all expert accounts (admin only)."""
    experts = _load_experts()
    return [
        {k: v for k, v in data.items() if k != "passwordHash" and k != "token"}
        for data in experts.values()
    ]


@router.put("/experts/{username}/status")
async def update_expert_status(username: str, status: str, _: str = Depends(verify_admin)):
    """Enable/disable an expert account (admin only)."""
    expert_file = _EXPERTS_DIR / f"{username}.json"
    if not expert_file.exists():
        raise HTTPException(404, "Expert not found")
    data = json.loads(expert_file.read_text())
    if status not in ("active", "disabled"):
        raise HTTPException(422, "Status must be 'active' or 'disabled'")
    data["status"] = status
    _save_expert(data)
    return {"username": username, "status": status}


@router.put("/experts/{username}/role")
async def update_expert_role(username: str, role: str, _: str = Depends(verify_admin)):
    """Change expert role (admin only). Roles: expert, senior, reviewer."""
    expert_file = _EXPERTS_DIR / f"{username}.json"
    if not expert_file.exists():
        raise HTTPException(404, "Expert not found")
    if role not in ("expert", "senior", "reviewer"):
        raise HTTPException(422, "Role must be 'expert', 'senior', or 'reviewer'")
    data = json.loads(expert_file.read_text())
    data["role"] = role
    _save_expert(data)
    return {"username": username, "role": role}


@router.delete("/experts/{username}")
async def delete_expert(username: str, _: str = Depends(verify_admin)):
    """Delete an expert account (admin only)."""
    expert_file = _EXPERTS_DIR / f"{username}.json"
    if not expert_file.exists():
        raise HTTPException(404, "Expert not found")
    expert_file.unlink()
    return {"status": "deleted", "username": username}


@router.get("/invite-codes")
async def list_all_invite_codes(_: str = Depends(verify_admin)):
    """List all invite codes (admin only)."""
    return _load_invites()


@router.post("/invite-codes/generate")
async def admin_generate_invite_codes(count: int = 1, _: str = Depends(verify_admin)):
    """Admin generates invite codes (no expert account needed)."""
    invites = _load_invites()
    new_codes = []
    for _ in range(min(count, 50)):
        code = secrets.token_urlsafe(12)
        invites.append({
            "code": code,
            "createdBy": "admin",
            "createdAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "used": False,
            "usedBy": None,
            "usedAt": None,
        })
        new_codes.append(code)
    _save_invites(invites)
    return {"codes": new_codes, "count": len(new_codes)}


class ExpertProposalInput(BaseModel):
    domain: str
    taskTitle: str
    difficulty: str
    context: str
    instruction: str
    requiredActions: List[str]
    successCriteria: str
    dataRequirements: Optional[str] = ""
    expertName: Optional[str] = ""
    expertEmail: Optional[str] = ""


class RevisionInput(BaseModel):
    notes: str


@router.post("/expert-proposals")
async def submit_expert_proposal(
    req: ExpertProposalInput,
    background_tasks: BackgroundTasks,
    username: str = Depends(verify_expert),
):
    """Accept a proposal, save it, and auto-trigger LLM generation."""
    proposal_id = f"{int(time.time())}-{uuid4().hex[:6]}"
    data = req.model_dump()
    data["_proposalId"] = proposal_id
    data["_submittedAt"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    data["_submittedBy"] = username
    data["_status"] = "generating"
    data["_revisions"] = []

    expert_file = _EXPERTS_DIR / f"{username}.json"
    if expert_file.exists():
        profile = json.loads(expert_file.read_text())
        data["_expertDisplayName"] = profile.get("displayName", "")
        data["_expertEmail"] = profile.get("email", "")
        data["_expertOrganization"] = profile.get("organization", "")
        data["_expertRole"] = profile.get("role", "expert")

    filepath = _PROPOSALS_DIR / f"{proposal_id}.json"
    filepath.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    background_tasks.add_task(_auto_generate, data, proposal_id)

    expert_file = _EXPERTS_DIR / f"{username}.json"
    if expert_file.exists():
        ed = json.loads(expert_file.read_text())
        ed["proposalCount"] = ed.get("proposalCount", 0) + 1
        _save_expert(ed)

    return {"status": "generating", "proposalId": proposal_id}


def _auto_generate(proposal_data: dict, proposal_id: str):
    """Auto-trigger LLM generation after expert submits."""
    try:
        from claw_bench.server.task_generator import _run_generation, _GENERATED_DIR
        gen_id = f"gen-{int(time.time())}-{uuid4().hex[:6]}"

        initial = {
            "taskId": "",
            "taskDirName": "",
            "proposalId": proposal_id,
            "domain": proposal_data.get("domain", ""),
            "taskTitle": proposal_data.get("taskTitle", ""),
            "difficulty": proposal_data.get("difficulty", ""),
            "status": "generating",
            "files": {},
            "generatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "error": None,
        }
        gen_file = _GENERATED_DIR / f"{gen_id}.json"
        gen_file.write_text(json.dumps(initial, indent=2, ensure_ascii=False))

        pf = _PROPOSALS_DIR / f"{proposal_id}.json"
        if pf.exists():
            pd = json.loads(pf.read_text())
            pd["_status"] = "generating"
            pd["_generatedTaskId"] = gen_id
            pf.write_text(json.dumps(pd, indent=2, ensure_ascii=False))

        _run_generation(proposal_data, gen_id)
    except Exception as e:
        import logging
        logging.getLogger(__name__).error("Auto-generate failed: %s", e)
        pf = _PROPOSALS_DIR / f"{proposal_id}.json"
        if pf.exists():
            pd = json.loads(pf.read_text())
            pd["_status"] = "error"
            pd["_error"] = str(e)
            pf.write_text(json.dumps(pd, indent=2, ensure_ascii=False))


@router.get("/expert-proposals/{proposal_id}/status")
async def get_proposal_status(proposal_id: str, username: str = Depends(verify_expert)):
    """Expert checks the status of their proposal (generating/ready/revision/confirmed)."""
    data = _verify_proposal_owner(proposal_id, username)
    gen_id = data.get("_generatedTaskId", "")

    result = {
        "proposalId": proposal_id,
        "status": data.get("_status", "pending"),
        "taskTitle": data.get("taskTitle", ""),
        "domain": data.get("domain", ""),
        "generatedTaskId": gen_id,
        "revisions": data.get("_revisions", []),
        "error": data.get("_error"),
    }

    if gen_id:
        from claw_bench.server.task_generator import _GENERATED_DIR
        gen_file = _GENERATED_DIR / f"{gen_id}.json"
        if gen_file.exists():
            gen_data = json.loads(gen_file.read_text())
            result["generationStatus"] = gen_data.get("status", "unknown")
            if gen_data.get("status") == "error":
                result["error"] = gen_data.get("error", "")
                result["status"] = "error"

    return result


@router.get("/expert-proposals/{proposal_id}/preview")
async def preview_generated_task(proposal_id: str, username: str = Depends(verify_expert)):
    """Expert previews the LLM-generated task files."""
    data = _verify_proposal_owner(proposal_id, username)
    gen_id = data.get("_generatedTaskId", "")
    if not gen_id:
        raise HTTPException(400, "No generated task yet")

    from claw_bench.server.task_generator import _GENERATED_DIR
    gen_file = _GENERATED_DIR / f"{gen_id}.json"
    if not gen_file.exists():
        raise HTTPException(404, "Generated task file not found")

    gen_data = json.loads(gen_file.read_text())
    if gen_data.get("status") == "generating":
        raise HTTPException(202, "Still generating, please wait")

    return {
        "proposalId": proposal_id,
        "taskId": gen_data.get("taskId", ""),
        "taskDirName": gen_data.get("taskDirName", ""),
        "domain": gen_data.get("domain", ""),
        "difficulty": gen_data.get("difficulty", ""),
        "status": gen_data.get("status", ""),
        "files": gen_data.get("files", {}),
        "error": gen_data.get("error"),
    }


@router.post("/expert-proposals/{proposal_id}/revise")
async def revise_proposal(
    proposal_id: str,
    req: RevisionInput,
    background_tasks: BackgroundTasks,
    username: str = Depends(verify_expert),
):
    """Expert requests revisions — adds notes and re-triggers generation."""
    data = _verify_proposal_owner(proposal_id, username)
    filepath = _PROPOSALS_DIR / f"{proposal_id}.json"
    revisions = data.get("_revisions", [])
    revisions.append({
        "notes": req.notes,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    })
    data["_revisions"] = revisions
    data["_status"] = "generating"
    data["context"] = data.get("context", "") + f"\n\n[Revision notes]: {req.notes}"
    filepath.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    background_tasks.add_task(_auto_generate, data, proposal_id)

    return {"status": "regenerating", "proposalId": proposal_id, "revisionCount": len(revisions)}


@router.post("/expert-proposals/{proposal_id}/confirm")
async def confirm_proposal(proposal_id: str, username: str = Depends(verify_expert)):
    """Expert confirms the generated task — moves it to admin approval queue."""
    data = _verify_proposal_owner(proposal_id, username)
    filepath = _PROPOSALS_DIR / f"{proposal_id}.json"
    gen_id = data.get("_generatedTaskId", "")
    if not gen_id:
        raise HTTPException(400, "No generated task to confirm")

    from claw_bench.server.task_generator import _GENERATED_DIR
    gen_file = _GENERATED_DIR / f"{gen_id}.json"
    if not gen_file.exists():
        raise HTTPException(404, "Generated task not found")

    gen_data = json.loads(gen_file.read_text())
    if gen_data.get("status") != "ready":
        raise HTTPException(400, f"Task not ready (status: {gen_data.get('status')})")

    data["_status"] = "confirmed"
    data["_confirmedAt"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    filepath.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    return {"status": "confirmed", "proposalId": proposal_id,
            "message": "Your task has been sent to the admin team for final approval."}


@router.get("/expert-proposals")
async def list_expert_proposals(_: str = Depends(verify_admin)):
    """List all expert proposals (admin only)."""
    proposals = []
    for f in sorted(_PROPOSALS_DIR.glob("*.json")):
        try:
            proposals.append(json.loads(f.read_text()))
        except (json.JSONDecodeError, OSError):
            continue
    return proposals


@router.delete("/expert-proposals/{proposal_id}")
async def delete_expert_proposal(proposal_id: str, _: str = Depends(verify_admin)):
    """Delete an expert proposal (admin only)."""
    filepath = _PROPOSALS_DIR / f"{proposal_id}.json"
    if not filepath.exists():
        raise HTTPException(404, f"Proposal {proposal_id} not found")
    filepath.unlink()
    return {"status": "deleted", "proposalId": proposal_id}


# ── Rebuild trigger ───────────────────────────────────────────────────────

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
