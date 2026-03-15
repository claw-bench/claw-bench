"""Public submission API with anti-abuse protections.

Rate limiting: per-IP, per-fingerprint, global daily cap.
Validation: schema check, score range check, duplicate detection.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from collections import defaultdict
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, field_validator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["submit"])

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
_DATA_DIR = _PROJECT_ROOT / "data"
_RESULTS_DIR = _DATA_DIR / "results"
_PENDING_DIR = _DATA_DIR / "pending"
_SUBMISSIONS_LOG = _DATA_DIR / "submissions.log"

for d in [_RESULTS_DIR, _PENDING_DIR]:
    try:
        d.mkdir(parents=True, exist_ok=True)
    except OSError:
        pass

# ── Rate Limiting State ──────────────────────────────────────────────

_lock = Lock()

_ip_submissions: Dict[str, List[float]] = defaultdict(list)
_fingerprint_submissions: Dict[str, List[float]] = defaultdict(list)
_daily_count: Dict[str, int] = defaultdict(int)
_daily_reset_day: str = ""

IP_MAX_PER_HOUR = 5
IP_MAX_PER_DAY = 15
FINGERPRINT_MAX_PER_DAY = 10
GLOBAL_MAX_PER_DAY = 500
MIN_INTERVAL_SECONDS = 30

_pending_hashes: set = set()


def _get_day() -> str:
    return time.strftime("%Y-%m-%d", time.gmtime())


def _cleanup_old(timestamps: List[float], window_s: float) -> List[float]:
    now = time.time()
    return [t for t in timestamps if now - t < window_s]


def _get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real_ip = request.headers.get("x-real-ip", "")
    if real_ip:
        return real_ip
    return request.client.host if request.client else "unknown"


def _check_rate_limits(ip: str, fingerprint: str) -> Optional[str]:
    global _daily_reset_day

    now = time.time()
    today = _get_day()

    with _lock:
        if today != _daily_reset_day:
            _daily_count.clear()
            _ip_submissions.clear()
            _fingerprint_submissions.clear()
            _daily_reset_day = today

        if sum(_daily_count.values()) >= GLOBAL_MAX_PER_DAY:
            return "Daily global submission limit reached. Please try again tomorrow."

        _ip_submissions[ip] = _cleanup_old(_ip_submissions[ip], 86400)
        ip_hour = [t for t in _ip_submissions[ip] if now - t < 3600]
        if len(ip_hour) >= IP_MAX_PER_HOUR:
            return f"Rate limit: max {IP_MAX_PER_HOUR} submissions per hour per IP."

        ip_day = _ip_submissions[ip]
        if len(ip_day) >= IP_MAX_PER_DAY:
            return f"Rate limit: max {IP_MAX_PER_DAY} submissions per day per IP."

        if _ip_submissions[ip] and now - _ip_submissions[ip][-1] < MIN_INTERVAL_SECONDS:
            wait = int(MIN_INTERVAL_SECONDS - (now - _ip_submissions[ip][-1])) + 1
            return f"Too fast. Please wait {wait} seconds before submitting again."

        if fingerprint:
            _fingerprint_submissions[fingerprint] = _cleanup_old(
                _fingerprint_submissions[fingerprint], 86400
            )
            if len(_fingerprint_submissions[fingerprint]) >= FINGERPRINT_MAX_PER_DAY:
                return f"Rate limit: max {FINGERPRINT_MAX_PER_DAY} submissions per day per device."

    return None


def _record_submission(ip: str, fingerprint: str):
    now = time.time()
    with _lock:
        _ip_submissions[ip].append(now)
        if fingerprint:
            _fingerprint_submissions[fingerprint].append(now)
        _daily_count[ip] = _daily_count.get(ip, 0) + 1


# ── Data Validation ──────────────────────────────────────────────────

class SubmitAgentProfile(BaseModel):
    displayName: str
    model: str
    framework: str
    skillsMode: str = "vanilla"
    skills: List[str] = []
    mcpServers: List[str] = []
    memoryModules: List[str] = []
    modelTier: Optional[str] = None


class SubmitProgressive(BaseModel):
    baseline_pass_rate: float = 0
    current_pass_rate: float = 0
    absolute_gain: float = 0
    normalized_gain: float = 0


class SubmissionRequest(BaseModel):
    framework: str = "unknown"
    model: str = "unknown"
    overall: float = 0
    taskCompletion: float = 0
    efficiency: float = 0
    security: float = 0
    skills: float = 0
    ux: float = 0
    testTier: Optional[str] = None
    agentProfile: Optional[SubmitAgentProfile] = None
    progressive: Optional[SubmitProgressive] = None
    fingerprint: Optional[str] = None
    tasksCompleted: Optional[int] = None
    clawId: Optional[str] = None
    tokensCost: Optional[float] = None
    customName: Optional[str] = None
    rawSummary: Optional[Dict] = None

    @field_validator("overall", "taskCompletion", "efficiency", "security", "skills", "ux")
    @classmethod
    def score_range(cls, v: float) -> float:
        if not (0 <= v <= 100):
            raise ValueError("Score must be between 0 and 100")
        return round(v, 2)

    @field_validator("framework", "model")
    @classmethod
    def non_empty(cls, v: str) -> str:
        v = v.strip()
        if not v or len(v) > 100:
            raise ValueError("Must be 1-100 characters")
        return v


def _compute_content_hash(data: dict) -> str:
    key_fields = f"{data['framework']}:{data['model']}:{data['overall']}:{data['taskCompletion']}"
    return hashlib.sha256(key_fields.encode()).hexdigest()[:16]


def _is_duplicate(data: dict) -> bool:
    content_hash = _compute_content_hash(data)
    if content_hash in _pending_hashes:
        return True
    for f in _RESULTS_DIR.glob("*.json"):
        try:
            existing = json.loads(f.read_text())
            if isinstance(existing, list):
                continue
            if _compute_content_hash(existing) == content_hash:
                return True
        except (json.JSONDecodeError, OSError, KeyError):
            continue
    return False


def _validate_score_consistency(data: dict) -> Optional[str]:
    """Weighted overall should roughly match the reported overall."""
    computed = (
        data["taskCompletion"] * 0.40
        + data["efficiency"] * 0.20
        + data["security"] * 0.15
        + data["skills"] * 0.15
        + data["ux"] * 0.10
    )
    diff = abs(computed - data["overall"])
    if diff > 15:
        return f"Score inconsistency: computed overall ({computed:.1f}) differs from reported ({data['overall']:.1f}) by {diff:.1f} points."
    return None


_last_rebuild_time: float = 0
_REBUILD_COOLDOWN = 60


def _trigger_rebuild_async():
    """Trigger frontend rebuild in background with 60s cooldown."""
    global _last_rebuild_time
    import subprocess
    import threading

    now = time.time()
    if now - _last_rebuild_time < _REBUILD_COOLDOWN:
        return
    _last_rebuild_time = now

    def _rebuild():
        try:
            leaderboard_dir = _PROJECT_ROOT / "leaderboard"
            subprocess.run(
                ["npm", "run", "build"],
                cwd=str(leaderboard_dir),
                capture_output=True,
                timeout=120,
            )
            logger.info("Frontend rebuilt after new submission")
        except Exception as e:
            logger.warning("Frontend rebuild failed: %s", e)

    threading.Thread(target=_rebuild, daemon=True).start()


def _has_cjk(text: str) -> bool:
    """Check if text contains Chinese/Japanese/Korean characters."""
    return any(0x4E00 <= ord(c) <= 0x9FFF or 0x3400 <= ord(c) <= 0x4DBF for c in text)


def _resolve_claw_id(explicit_id: Optional[str], nickname: str, fingerprint: str) -> str:
    """Derive a stable clawId from nickname + device fingerprint.

    Same nickname + same device → always the same clawId, regardless of model.
    If the user provides an explicit --claw-id, use that instead.
    """
    if explicit_id:
        return explicit_id
    if nickname and fingerprint:
        raw = f"{nickname}:{fingerprint[:16]}"
        return hashlib.sha256(raw.encode()).hexdigest()[:12]
    if nickname:
        slug = nickname.lower().replace(" ", "-")
        return hashlib.sha256(slug.encode()).hexdigest()[:12]
    if fingerprint:
        return hashlib.sha256(fingerprint.encode()).hexdigest()[:12]
    return uuid4().hex[:8]


def _compute_rank(overall: float, test_tier: Optional[str] = None) -> tuple:
    """Compute global rank and tier rank. Returns (rank, total, tier_rank, tier_total)."""
    all_scores = []
    tier_scores = []
    for f in _RESULTS_DIR.glob("*.json"):
        try:
            d = json.loads(f.read_text())
            if isinstance(d, dict) and "overall" in d:
                score = d["overall"]
                all_scores.append(score)
                if test_tier and d.get("testTier") == test_tier:
                    tier_scores.append(score)
        except (json.JSONDecodeError, OSError):
            continue
    all_scores.sort(reverse=True)
    tier_scores.sort(reverse=True)
    rank = next((i + 1 for i, s in enumerate(all_scores) if s <= overall), len(all_scores) + 1)
    tier_rank = next((i + 1 for i, s in enumerate(tier_scores) if s <= overall), len(tier_scores) + 1) if tier_scores else 0
    return rank, len(all_scores), tier_rank, len(tier_scores)


def _log_submission(ip: str, fingerprint: str, data: dict, status: str, reason: str = ""):
    try:
        entry = {
            "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "ip": ip,
            "fingerprint": fingerprint[:12] if fingerprint else "",
            "framework": data.get("framework", ""),
            "model": data.get("model", ""),
            "overall": data.get("overall", 0),
            "status": status,
            "reason": reason,
        }
        with open(_SUBMISSIONS_LOG, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except OSError:
        pass


# ── Submit Endpoint ──────────────────────────────────────────────────

@router.post("/submit")
async def submit_results(req: SubmissionRequest, request: Request):
    """Public endpoint for submitting benchmark results.

    Features:
    - Auto-detect region from IP (Taiwan/HK/Macau handled separately)
    - Same clawId can submit multiple times (best score kept, count tracked)
    - Anti-abuse: IP/fingerprint rate limiting, score validation, duplicate detection
    """
    from claw_bench.server.geoip import lookup_ip, get_flag

    ip = _get_client_ip(request)
    fingerprint = req.fingerprint or ""

    if req.rawSummary:
        raw = req.rawSummary
        scores = raw.get("scores", {})
        profile = raw.get("agent_profile") or raw.get("agentProfile") or {}
        req.framework = raw.get("framework", req.framework)
        req.model = raw.get("model", req.model)
        req.overall = raw.get("overall", scores.get("overall", req.overall))
        req.taskCompletion = raw.get("taskCompletion", scores.get("task_completion", req.taskCompletion))
        req.efficiency = raw.get("efficiency", scores.get("efficiency", req.efficiency))
        req.security = raw.get("security", scores.get("security", req.security))
        req.skills = raw.get("skills", raw.get("skills_efficacy", scores.get("skills_efficacy", req.skills)))
        req.ux = raw.get("ux", raw.get("ux_engineering", scores.get("ux_engineering", req.ux)))
        req.testTier = raw.get("testTier", raw.get("test_tier", req.testTier))
        req.tasksCompleted = scores.get("tasks_total", req.tasksCompleted)
        if profile and not req.agentProfile:
            req.agentProfile = SubmitAgentProfile(
                displayName=profile.get("displayName", profile.get("display_name", "")),
                model=profile.get("model", req.model),
                framework=profile.get("framework", req.framework),
                skillsMode=profile.get("skillsMode", profile.get("skills_mode", "vanilla")),
                skills=profile.get("skills", []),
                mcpServers=profile.get("mcpServers", profile.get("mcp_servers", [])),
                memoryModules=profile.get("memoryModules", profile.get("memory_modules", [])),
                modelTier=profile.get("modelTier", profile.get("model_tier")),
            )
        if raw.get("progressive"):
            req.progressive = SubmitProgressive(**{k: v for k, v in raw["progressive"].items() if k in SubmitProgressive.model_fields})

    if req.rawSummary and req.overall > 0 and req.taskCompletion == 0:
        req.taskCompletion = req.overall
        req.efficiency = req.overall * 0.85
        req.security = req.overall * 0.80
        req.skills = req.overall * 0.75
        req.ux = req.overall * 0.80

    if req.framework in ("unknown", "") or req.overall <= 0:
        _log_submission(ip, fingerprint, {"framework": req.framework, "overall": req.overall}, "rejected", "Empty data")
        raise HTTPException(422, "Invalid submission: framework is required and overall score must be > 0.")

    raw_model = req.model or "unknown"
    if "/" in raw_model:
        req.model = raw_model.rsplit("/", 1)[-1]

    data = req.model_dump(exclude={"fingerprint", "clawId", "customName", "rawSummary"})
    claw_id = req.clawId

    rate_error = _check_rate_limits(ip, fingerprint)
    if rate_error:
        _log_submission(ip, fingerprint, data, "rejected", rate_error)
        raise HTTPException(429, rate_error)

    consistency_error = _validate_score_consistency(data)
    if consistency_error:
        _log_submission(ip, fingerprint, data, "rejected", consistency_error)
        raise HTTPException(422, consistency_error)

    country_code, country_name = await lookup_ip(ip)
    flag = get_flag(country_code)
    now_str = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    custom_name = req.customName or ""
    framework = data.get("framework", "unknown")
    model = data.get("model", "unknown")

    resolved_id = _resolve_claw_id(claw_id, custom_name, fingerprint)

    existing_file = _find_claw_file(resolved_id)
    if existing_file:
        return await _update_existing_claw(
            existing_file, data, country_code, country_name, flag,
            now_str, ip, fingerprint, custom_name,
        )

    if custom_name:
        already_has_framework = framework.lower() in custom_name.lower() or "claw" in custom_name.lower()
        if already_has_framework:
            display = custom_name
        elif _has_cjk(custom_name):
            display = f"{custom_name}的{framework}"
        else:
            display = f"{custom_name}'s {framework}"
    else:
        display = f"{framework} / {model}"

    profile_id = resolved_id
    if data.get("agentProfile"):
        data["agentProfile"]["profileId"] = profile_id
        data["agentProfile"]["displayName"] = display
    else:
        data["agentProfile"] = {
            "profileId": profile_id,
            "displayName": display,
            "model": model,
            "framework": framework,
            "skillsMode": "vanilla",
            "skills": [], "mcpServers": [], "memoryModules": [],
            "modelTier": None, "tags": {},
        }

    data["region"] = {"code": country_code, "name": country_name, "flag": flag}
    data["submissionCount"] = 1
    data["lastUpdated"] = now_str
    data["clawId"] = profile_id
    data["modelsUsed"] = [model]

    safe_name = f"{data['framework']}-{data['model']}-{profile_id}".replace("/", "-").replace(" ", "_")
    filename = f"{safe_name}.json"
    filepath = _RESULTS_DIR / filename

    content_hash = _compute_content_hash(data)
    _pending_hashes.add(content_hash)

    try:
        filepath.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    except OSError as e:
        _pending_hashes.discard(content_hash)
        _log_submission(ip, fingerprint, data, "error", str(e))
        raise HTTPException(500, "Failed to save results.")

    _record_submission(ip, fingerprint)
    _log_submission(ip, fingerprint, data, "accepted")

    rank, total, tier_rank, tier_total = _compute_rank(data["overall"], data.get("testTier"))

    logger.info("Submission live: %s rank #%d from %s (%s %s)", filename, rank, ip, flag, country_name)

    _trigger_rebuild_async()

    return {
        "status": "live",
        "clawId": profile_id,
        "filename": filename,
        "region": f"{flag} {country_name}",
        "rank": rank,
        "totalEntries": total,
        "tierRank": tier_rank,
        "tierTotal": tier_total,
        "testTier": data.get("testTier", ""),
        "message": f"Results are now live on the leaderboard! Rank: #{rank} of {total}",
    }


def _find_claw_file(claw_id: str) -> Optional[Path]:
    """Find existing result file for a clawId."""
    for f in _RESULTS_DIR.glob("*.json"):
        try:
            d = json.loads(f.read_text())
            if isinstance(d, dict) and d.get("clawId") == claw_id:
                return f
        except (json.JSONDecodeError, OSError):
            continue
    return None


async def _update_existing_claw(
    filepath: Path, new_data: dict,
    country_code: str, country_name: str, flag: str,
    now_str: str, ip: str, fingerprint: str,
    custom_name: str = "",
) -> dict:
    """Update existing Claw record directly (best score kept, models tracked)."""
    try:
        existing = json.loads(filepath.read_text())
    except (json.JSONDecodeError, OSError):
        existing = {}

    claw_id = existing.get("clawId", "")
    old_count = existing.get("submissionCount", 1)
    new_count = old_count + 1
    old_overall = existing.get("overall", 0)
    new_overall = new_data.get("overall", 0)
    new_model = new_data.get("model", "")
    framework = new_data.get("framework", existing.get("framework", ""))

    models_used = existing.get("modelsUsed", [])
    if new_model and new_model not in models_used:
        models_used.append(new_model)
    existing["modelsUsed"] = models_used

    if new_overall > old_overall:
        for k in ("overall", "taskCompletion", "efficiency", "security", "skills", "ux", "testTier", "tokensCost"):
            if k in new_data:
                existing[k] = new_data[k]
        existing["model"] = new_model
        existing["framework"] = framework
        if new_data.get("agentProfile"):
            existing["agentProfile"] = new_data["agentProfile"]
            existing["agentProfile"]["profileId"] = claw_id
        if new_data.get("progressive"):
            existing["progressive"] = new_data["progressive"]
        best_model = new_model
        status_msg = f"New high score! {old_overall:.1f} → {new_overall:.1f} (model: {new_model})"
    else:
        best_model = existing.get("model", new_model)
        status_msg = f"Score {new_overall:.1f} did not beat best {old_overall:.1f}. Count updated."

    if custom_name:
        already_has_framework = framework.lower() in custom_name.lower() or "claw" in custom_name.lower()
        if already_has_framework:
            display = custom_name
        elif _has_cjk(custom_name):
            display = f"{custom_name}的{framework}"
        else:
            display = f"{custom_name}'s {framework}"
        if existing.get("agentProfile"):
            existing["agentProfile"]["displayName"] = display

    existing["region"] = {"code": country_code, "name": country_name, "flag": flag}
    existing["submissionCount"] = new_count
    existing["lastUpdated"] = now_str

    filepath.write_text(json.dumps(existing, indent=2, ensure_ascii=False))

    _record_submission(ip, fingerprint)
    _log_submission(ip, fingerprint, new_data, "updated", f"clawId={claw_id} count={new_count}")

    rank, total, tier_rank, tier_total = _compute_rank(
        max(old_overall, new_overall), existing.get("testTier")
    )

    _trigger_rebuild_async()

    return {
        "status": "updated",
        "clawId": claw_id,
        "submissionCount": new_count,
        "region": f"{flag} {country_name}",
        "rank": rank,
        "totalEntries": total,
        "tierRank": tier_rank,
        "tierTotal": tier_total,
        "message": status_msg,
    }


@router.get("/submit/status")
async def submit_status():
    """Check submission system status and limits."""
    today = _get_day()
    with _lock:
        total_today = sum(_daily_count.values()) if _daily_reset_day == today else 0
    return {
        "status": "open" if total_today < GLOBAL_MAX_PER_DAY else "closed",
        "submissions_today": total_today,
        "daily_limit": GLOBAL_MAX_PER_DAY,
        "per_ip_hourly": IP_MAX_PER_HOUR,
        "per_ip_daily": IP_MAX_PER_DAY,
        "per_device_daily": FINGERPRINT_MAX_PER_DAY,
        "min_interval_seconds": MIN_INTERVAL_SECONDS,
    }
