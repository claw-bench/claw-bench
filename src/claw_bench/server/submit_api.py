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


class TaskResultItem(BaseModel):
    taskId: str
    passed: bool = False
    score: float = 0.0


TASK_ID_TO_DOMAIN: Dict[str, str] = {
    "cal-001": "calendar",
    "cal-002": "calendar",
    "cal-003": "calendar",
    "cal-004": "calendar",
    "cal-005": "calendar",
    "cal-006": "calendar",
    "cal-007": "calendar",
    "cal-008": "calendar",
    "cal-009": "calendar",
    "cal-010": "calendar",
    "cal-011": "calendar",
    "cal-012": "calendar",
    "cal-013": "calendar",
    "cal-014": "calendar",
    "cal-015": "calendar",
    "code-001": "code-assistance",
    "code-002": "code-assistance",
    "code-003": "code-assistance",
    "code-004": "code-assistance",
    "code-005": "code-assistance",
    "code-006": "code-assistance",
    "code-007": "code-assistance",
    "code-008": "code-assistance",
    "code-009": "code-assistance",
    "code-010": "code-assistance",
    "code-011": "code-assistance",
    "code-012": "code-assistance",
    "code-013": "code-assistance",
    "code-014": "code-assistance",
    "code-015": "code-assistance",
    "comm-001": "communication",
    "comm-002": "communication",
    "comm-003": "communication",
    "comm-004": "communication",
    "comm-005": "communication",
    "comm-006": "communication",
    "comm-007": "communication",
    "comm-008": "communication",
    "comm-009": "communication",
    "comm-010": "communication",
    "comm-011": "communication",
    "comm-012": "communication",
    "comm-013": "communication",
    "comm-014": "communication",
    "comm-015": "communication",
    "data-001": "data-analysis",
    "data-002": "data-analysis",
    "data-003": "data-analysis",
    "data-004": "data-analysis",
    "data-005": "data-analysis",
    "data-006": "data-analysis",
    "data-007": "data-analysis",
    "data-008": "data-analysis",
    "data-009": "data-analysis",
    "data-010": "data-analysis",
    "data-011": "data-analysis",
    "data-012": "data-analysis",
    "data-013": "data-analysis",
    "data-014": "data-analysis",
    "data-015": "data-analysis",
    "data-016": "data-analysis",
    "data-017": "data-analysis",
    "doc-001": "document-editing",
    "doc-002": "document-editing",
    "doc-003": "document-editing",
    "doc-004": "document-editing",
    "doc-005": "document-editing",
    "doc-006": "document-editing",
    "doc-007": "document-editing",
    "doc-008": "document-editing",
    "doc-009": "document-editing",
    "doc-010": "document-editing",
    "doc-011": "document-editing",
    "doc-012": "document-editing",
    "doc-013": "document-editing",
    "doc-014": "document-editing",
    "doc-015": "document-editing",
    "doc-016": "document-editing",
    "doc-017": "document-editing",
    "doc-018": "document-editing",
    "eml-001": "email",
    "eml-002": "email",
    "eml-003": "email",
    "eml-004": "email",
    "eml-005": "email",
    "eml-006": "email",
    "eml-007": "email",
    "eml-008": "email",
    "eml-009": "email",
    "eml-010": "email",
    "eml-011": "email",
    "eml-012": "email",
    "eml-013": "email",
    "eml-014": "email",
    "eml-015": "email",
    "eml-016": "email",
    "eml-017": "email",
    "eml-018": "email",
    "file-001": "file-operations",
    "file-002": "file-operations",
    "file-003": "file-operations",
    "file-004": "file-operations",
    "file-005": "file-operations",
    "file-006": "file-operations",
    "file-007": "file-operations",
    "file-008": "file-operations",
    "file-009": "file-operations",
    "file-010": "file-operations",
    "file-011": "file-operations",
    "file-012": "file-operations",
    "file-013": "file-operations",
    "file-014": "file-operations",
    "file-015": "file-operations",
    "mem-001": "memory",
    "mem-002": "memory",
    "mem-003": "memory",
    "mem-004": "memory",
    "mem-005": "memory",
    "mem-006": "memory",
    "mem-007": "memory",
    "mem-008": "memory",
    "mem-009": "memory",
    "mem-010": "memory",
    "mem-011": "memory",
    "mem-012": "memory",
    "mem-013": "memory",
    "mem-014": "memory",
    "mem-015": "memory",
    "mm-001": "multimodal",
    "mm-002": "multimodal",
    "mm-003": "multimodal",
    "mm-004": "multimodal",
    "mm-005": "multimodal",
    "mm-006": "multimodal",
    "mm-007": "multimodal",
    "mm-008": "multimodal",
    "mm-009": "multimodal",
    "mm-010": "multimodal",
    "mm-011": "multimodal",
    "mm-012": "multimodal",
    "mm-013": "multimodal",
    "mm-014": "multimodal",
    "mm-015": "multimodal",
    "sec-001": "security",
    "sec-002": "security",
    "sec-003": "security",
    "sec-004": "security",
    "sec-005": "security",
    "sec-006": "security",
    "sec-007": "security",
    "sec-008": "security",
    "sec-009": "security",
    "sec-010": "security",
    "sec-011": "security",
    "sec-012": "security",
    "sec-013": "security",
    "sec-014": "security",
    "sec-015": "security",
    "sys-001": "system-admin",
    "sys-002": "system-admin",
    "sys-003": "system-admin",
    "sys-004": "system-admin",
    "sys-005": "system-admin",
    "sys-006": "system-admin",
    "sys-007": "system-admin",
    "sys-008": "system-admin",
    "sys-009": "system-admin",
    "sys-010": "system-admin",
    "sys-011": "system-admin",
    "sys-012": "system-admin",
    "sys-013": "system-admin",
    "sys-014": "system-admin",
    "sys-015": "system-admin",
    "web-001": "web-browsing",
    "web-002": "web-browsing",
    "web-003": "web-browsing",
    "web-004": "web-browsing",
    "web-005": "web-browsing",
    "web-006": "web-browsing",
    "web-007": "web-browsing",
    "web-008": "web-browsing",
    "web-009": "web-browsing",
    "web-010": "web-browsing",
    "web-011": "web-browsing",
    "web-012": "web-browsing",
    "web-013": "web-browsing",
    "web-014": "web-browsing",
    "web-015": "web-browsing",
    "wfl-001": "workflow-automation",
    "wfl-002": "workflow-automation",
    "wfl-003": "workflow-automation",
    "wfl-004": "workflow-automation",
    "wfl-005": "workflow-automation",
    "wfl-006": "workflow-automation",
    "wfl-007": "workflow-automation",
    "wfl-008": "workflow-automation",
    "wfl-009": "workflow-automation",
    "wfl-010": "workflow-automation",
    "wfl-011": "workflow-automation",
    "wfl-012": "workflow-automation",
    "wfl-013": "workflow-automation",
    "wfl-014": "workflow-automation",
    "wfl-015": "workflow-automation",
    "wfl-016": "workflow-automation",
    "wfl-017": "workflow-automation",
    "xdom-001": "cross-domain",
    "xdom-002": "cross-domain",
    "xdom-003": "cross-domain",
    "xdom-004": "cross-domain",
    "xdom-005": "cross-domain",
    "xdom-006": "cross-domain",
    "xdom-007": "cross-domain",
    "xdom-008": "cross-domain",
    "xdom-009": "cross-domain",
    "xdom-010": "cross-domain",
    "xdom-011": "cross-domain",
    "xdom-012": "cross-domain",
    "xdom-013": "cross-domain",
    "xdom-014": "cross-domain",
    "xdom-015": "cross-domain",
    "xdom-016": "cross-domain",
    "xdom-017": "cross-domain",
    "debug-001": "debugging",
    "debug-002": "debugging",
    "debug-003": "debugging",
    "debug-004": "debugging",
    "debug-005": "debugging",
    "db-001": "database",
    "db-002": "database",
    "db-003": "database",
    "db-004": "database",
    "db-005": "database",
    "plan-001": "planning",
    "plan-002": "planning",
    "plan-003": "planning",
    "plan-004": "planning",
    "plan-005": "planning",
    "math-001": "math-reasoning",
    "math-002": "math-reasoning",
    "math-003": "math-reasoning",
    "math-004": "math-reasoning",
    "math-005": "math-reasoning",
    "tool-001": "real-tools",
    "tool-002": "real-tools",
    "tool-003": "real-tools",
    "tool-004": "real-tools",
    "tool-005": "real-tools",
    # Subject-matter domains (65 tasks)
    "acad-001-citation-network": "academic-research",
    "acad-002-literature-review": "academic-research",
    "acad-003-statistical-analysis": "academic-research",
    "acad-004-plagiarism-check": "academic-research",
    "acad-005-metadata-extraction": "academic-research",
    "acct-001-journal-entries": "accounting",
    "acct-002-trial-balance": "accounting",
    "acct-003-depreciation": "accounting",
    "acct-004-bank-reconciliation": "accounting",
    "acct-005-financial-statements": "accounting",
    "bio-001-sequence-analysis": "bioinformatics",
    "bio-002-protein-alignment": "bioinformatics",
    "bio-003-gene-expression": "bioinformatics",
    "bio-004-phylogenetic": "bioinformatics",
    "bio-005-variant-annotation": "bioinformatics",
    "med-001-patient-deidentify": "clinical-data",
    "med-002-lab-abnormality": "clinical-data",
    "med-003-drug-interaction": "clinical-data",
    "med-004-icd-coding": "clinical-data",
    "med-005-trial-eligibility": "clinical-data",
    "cont-001-sentiment-analysis": "content-analysis",
    "cont-002-topic-modeling": "content-analysis",
    "cont-003-readability-audit": "content-analysis",
    "cont-004-media-bias": "content-analysis",
    "cont-005-translation-qa": "content-analysis",
    "law-001-nda-clause-extract": "contract-review",
    "law-002-lease-analysis": "contract-review",
    "law-003-compliance-check": "contract-review",
    "law-004-ip-license-review": "contract-review",
    "law-005-merger-due-diligence": "contract-review",
    "cs-001-api-rate-limiter": "cs-engineering",
    "cs-002-db-migration": "cs-engineering",
    "cs-003-log-analyzer": "cs-engineering",
    "cs-004-ci-pipeline": "cs-engineering",
    "cs-005-api-design": "cs-engineering",
    "ds-001-customer-segmentation": "data-science",
    "ds-002-ab-testing": "data-science",
    "ds-003-feature-engineering": "data-science",
    "ds-004-time-series": "data-science",
    "ds-005-anomaly-detection": "data-science",
    "edu-001-rubric-grading": "educational-assessment",
    "edu-002-item-analysis": "educational-assessment",
    "edu-003-learning-path": "educational-assessment",
    "edu-004-curriculum-mapping": "educational-assessment",
    "edu-005-assessment-generation": "educational-assessment",
    "fin-001-portfolio-beta": "financial-analysis",
    "fin-002-dcf-valuation": "financial-analysis",
    "fin-003-risk-metrics": "financial-analysis",
    "fin-004-earnings-report": "financial-analysis",
    "fin-005-forex-arbitrage": "financial-analysis",
    "fin-006": "financial-analysis",
    "fin-007": "financial-analysis",
    "fin-008": "financial-analysis",
    "edu-001": "education",
    "mkt-001-survey-analysis": "market-research",
    "mkt-002-competitor-matrix": "market-research",
    "mkt-003-pricing-analysis": "market-research",
    "mkt-004-trend-extraction": "market-research",
    "mkt-005-market-sizing": "market-research",
    "reg-001-gdpr-audit": "regulatory-compliance",
    "reg-002-sox-controls": "regulatory-compliance",
    "reg-003-aml-screening": "regulatory-compliance",
    "reg-004-hipaa-assessment": "regulatory-compliance",
    "reg-005-environmental-report": "regulatory-compliance",
    "sci-001-ode-solver": "scientific-computing",
    "sci-002-monte-carlo": "scientific-computing",
    "sci-003-matrix-decomposition": "scientific-computing",
    "sci-004-signal-processing": "scientific-computing",
    "sci-005-optimization": "scientific-computing",
}

DOMAIN_TO_DIMENSION: Dict[str, str] = {
    # Foundation domains
    "file-operations": "efficiency",
    "data-analysis": "efficiency",
    "workflow-automation": "efficiency",
    "database": "efficiency",
    "real-tools": "efficiency",
    "security": "security",
    "system-admin": "security",
    "code-assistance": "skills",
    "cross-domain": "skills",
    "multimodal": "skills",
    "debugging": "skills",
    "math-reasoning": "skills",
    "communication": "ux",
    "email": "ux",
    "calendar": "ux",
    "document-editing": "ux",
    "memory": "ux",
    "web-browsing": "ux",
    "planning": "ux",
    "multi-agent": "skills",
    # Subject-matter domains
    "accounting": "efficiency",
    "financial-analysis": "efficiency",
    "data-science": "efficiency",
    "scientific-computing": "skills",
    "cs-engineering": "skills",
    "bioinformatics": "skills",
    "contract-review": "security",
    "regulatory-compliance": "security",
    "clinical-data": "security",
    "content-analysis": "ux",
    "market-research": "ux",
    "educational-assessment": "ux",
    "academic-research": "ux",
    "education": "ux",
}

def _scan_tasks_from_disk():
    """Scan tasks/ directory and add any task IDs not already in TASK_ID_TO_DOMAIN."""
    tasks_root = _PROJECT_ROOT / "tasks"
    if not tasks_root.is_dir():
        return
    try:
        import tomli
    except ImportError:
        return
    added = 0
    for toml_file in tasks_root.rglob("task.toml"):
        try:
            with open(toml_file, "rb") as f:
                t = tomli.load(f)
            if "task" in t and isinstance(t["task"], dict):
                t.update(t.pop("task"))
            tid = t.get("id", "")
            domain = t.get("domain", toml_file.parent.parent.name)
            if tid and tid not in TASK_ID_TO_DOMAIN:
                TASK_ID_TO_DOMAIN[tid] = domain
                if domain not in DOMAIN_TO_DIMENSION:
                    DOMAIN_TO_DIMENSION[domain] = "skills"
                added += 1
        except Exception:
            continue
    if added > 0:
        logger.info("Scanned disk: added %d new task IDs (total %d)", added, len(TASK_ID_TO_DOMAIN))

_scan_tasks_from_disk()

VALID_TASK_IDS = set(TASK_ID_TO_DOMAIN.keys())


def refresh_task_registry():
    """Re-scan disk and update VALID_TASK_IDS + domains.json. Safe to call anytime."""
    global VALID_TASK_IDS
    _scan_tasks_from_disk()
    VALID_TASK_IDS = set(TASK_ID_TO_DOMAIN.keys())

    _sync_domains_json()

    return len(VALID_TASK_IDS)


def _sync_domains_json():
    """Regenerate data/config/domains.json from TASK_ID_TO_DOMAIN."""
    domains_file = _DATA_DIR / "config" / "domains.json"
    try:
        import tomli
    except ImportError:
        return

    domain_stats: Dict[str, Dict[str, int]] = {}
    tasks_root = _PROJECT_ROOT / "tasks"
    for toml_file in tasks_root.rglob("task.toml"):
        try:
            with open(toml_file, "rb") as f:
                t = tomli.load(f)
            if "task" in t and isinstance(t["task"], dict):
                t.update(t.pop("task"))
            domain = t.get("domain", toml_file.parent.parent.name)
            level = t.get("level", "L1").lower()
            if domain not in domain_stats:
                domain_stats[domain] = {"tasks": 0, "l1": 0, "l2": 0, "l3": 0, "l4": 0}
            domain_stats[domain]["tasks"] += 1
            if level in domain_stats[domain]:
                domain_stats[domain][level] += 1
        except Exception:
            continue

    existing_names: Dict[str, str] = {}
    if domains_file.exists():
        try:
            for d in json.loads(domains_file.read_text()):
                existing_names[d["id"]] = d.get("name", d["id"])
        except Exception:
            pass

    result = []
    for did in sorted(domain_stats.keys()):
        s = domain_stats[did]
        name = existing_names.get(did, did.replace("-", " ").title())
        result.append({"id": did, "name": name, "tasks": s["tasks"],
                       "l1": s["l1"], "l2": s["l2"], "l3": s["l3"], "l4": s["l4"]})

    domains_file.parent.mkdir(parents=True, exist_ok=True)
    domains_file.write_text(json.dumps(result, indent=2, ensure_ascii=False))

    # Also update skill.md numbers
    import re
    total = sum(s["tasks"] for s in domain_stats.values())
    doms = len(domain_stats)
    for md_path in [_PROJECT_ROOT / "skills" / "skill.md",
                    _PROJECT_ROOT / "leaderboard" / "public" / "skill.md"]:
        if md_path.exists():
            try:
                text = md_path.read_text()
                text = re.sub(r"全部 \d+ 任务", f"全部 {total} 任务", text)
                text = re.sub(r"\d+ domains, \d+ tasks\)", f"{doms} domains, {total} tasks)", text)
                text = re.sub(r"Full test = all \d+ tasks", f"Full test = all {total} tasks", text)
                text = re.sub(r"~\d+ tasks, plan for", f"~{total} tasks, plan for", text)
                md_path.write_text(text)
            except Exception:
                pass


SUBJECT_MATTER_DOMAINS = {
    "accounting", "financial-analysis", "data-science", "scientific-computing",
    "cs-engineering", "bioinformatics", "contract-review", "regulatory-compliance",
    "clinical-data", "content-analysis", "market-research", "educational-assessment",
    "academic-research",
}


def _compute_dual_track_scores(task_results: List[TaskResultItem]) -> Dict[str, float]:
    """Compute foundation score, subject-matter score, and breakdown by subject domain."""
    foundation_scores: List[float] = []
    subject_scores: List[float] = []
    subject_breakdown: Dict[str, List[float]] = {}

    for tr in task_results:
        domain = TASK_ID_TO_DOMAIN.get(tr.taskId)
        if not domain:
            continue
        if domain in SUBJECT_MATTER_DOMAINS:
            subject_scores.append(tr.score)
            subject_breakdown.setdefault(domain, []).append(tr.score)
        else:
            foundation_scores.append(tr.score)

    result: Dict[str, Any] = {}
    result["foundationScore"] = round((sum(foundation_scores) / len(foundation_scores) * 100) if foundation_scores else 0, 2)
    result["subjectScore"] = round((sum(subject_scores) / len(subject_scores) * 100) if subject_scores else 0, 2)
    result["subjectBreakdown"] = {
        dom: round(sum(scores) / len(scores) * 100, 2)
        for dom, scores in subject_breakdown.items()
    } if subject_breakdown else {}

    return result


def _compute_dimension_scores(task_results: List[TaskResultItem]) -> Dict[str, float]:
    """Compute real 5-dimension scores from per-task results grouped by domain."""
    dim_scores: Dict[str, List[float]] = {"efficiency": [], "security": [], "skills": [], "ux": []}

    for tr in task_results:
        domain = TASK_ID_TO_DOMAIN.get(tr.taskId)
        if not domain:
            continue
        dimension = DOMAIN_TO_DIMENSION.get(domain)
        if dimension and dimension in dim_scores:
            dim_scores[dimension].append(tr.score)

    result = {}
    for dim, scores in dim_scores.items():
        result[dim] = round((sum(scores) / len(scores) * 100) if scores else 0, 2)

    fully_passed = sum(1 for tr in task_results if tr.passed)
    result["taskCompletion"] = round((fully_passed / len(task_results) * 100) if task_results else 0, 2)

    return result


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
    taskResults: Optional[List[TaskResultItem]] = None

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

    if req.taskResults and len(req.taskResults) > 0:
        invalid_ids = [tr.taskId for tr in req.taskResults if tr.taskId not in VALID_TASK_IDS]
        valid_results = [tr for tr in req.taskResults if tr.taskId in VALID_TASK_IDS]
        for tr in valid_results:
            tr.score = max(0.0, min(1.0, tr.score))

        if len(valid_results) < 3:
            _log_submission(ip, fingerprint, {"framework": req.framework}, "rejected", f"Too few valid tasks: {len(valid_results)}")
            raise HTTPException(422, f"Need at least 3 valid task results. Got {len(valid_results)} valid, {len(invalid_ids)} invalid IDs.")

        dim = _compute_dimension_scores(valid_results)
        req.taskCompletion = dim["taskCompletion"]
        req.efficiency = dim["efficiency"]
        req.security = dim["security"]
        req.skills = dim["skills"]
        req.ux = dim["ux"]

        total_scores = [tr.score for tr in valid_results]
        req.overall = round(sum(total_scores) / len(total_scores) * 100, 2)
        req.tasksCompleted = len(valid_results)

    elif req.rawSummary and req.overall > 0 and req.taskCompletion == 0:
        pass

    if req.framework in ("unknown", "") or req.overall <= 0:
        _log_submission(ip, fingerprint, {"framework": req.framework, "overall": req.overall}, "rejected", "Empty data")
        raise HTTPException(422, "Invalid submission: framework is required and overall score must be > 0.")

    raw_model = req.model or "unknown"
    if "/" in raw_model:
        req.model = raw_model.rsplit("/", 1)[-1]

    data = req.model_dump(exclude={"fingerprint", "clawId", "customName", "rawSummary"})
    if req.taskResults:
        valid_for_dual = [tr for tr in req.taskResults if tr.taskId in VALID_TASK_IDS]
        data["taskResults"] = [{"taskId": tr.taskId, "passed": tr.passed, "score": round(tr.score, 4)} for tr in valid_for_dual]
        dual_scores = _compute_dual_track_scores(valid_for_dual)
        data["foundationScore"] = dual_scores.get("foundationScore", 0)
        data["subjectScore"] = dual_scores.get("subjectScore", 0)
        data["subjectBreakdown"] = dual_scores.get("subjectBreakdown", {})
    claw_id = req.clawId

    rate_error = _check_rate_limits(ip, fingerprint)
    if rate_error:
        _log_submission(ip, fingerprint, data, "rejected", rate_error)
        raise HTTPException(429, rate_error)

    if not req.taskResults and not req.rawSummary:
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
        "scores": {
            "overall": data.get("overall", 0),
            "taskCompletion": data.get("taskCompletion", 0),
            "efficiency": data.get("efficiency", 0),
            "security": data.get("security", 0),
            "skills": data.get("skills", 0),
            "ux": data.get("ux", 0),
            "foundationScore": data.get("foundationScore", 0),
            "subjectScore": data.get("subjectScore", 0),
            "subjectBreakdown": data.get("subjectBreakdown", {}),
        },
        "tasksAccepted": len(data.get("taskResults", []) or []),
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

    old_task_count = len(existing.get("taskResults", []) or [])
    new_task_count = len(new_data.get("taskResults", []) or [])
    should_update = new_overall >= old_overall or new_task_count > old_task_count

    if should_update:
        for k in ("overall", "taskCompletion", "efficiency", "security", "skills", "ux",
                   "testTier", "tokensCost", "taskResults", "foundationScore", "subjectScore", "subjectBreakdown"):
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
        status_msg = f"Updated: {old_overall:.1f} → {new_overall:.1f} (tasks: {old_task_count} → {new_task_count})"
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
        "scores": {
            "overall": existing.get("overall", 0),
            "taskCompletion": existing.get("taskCompletion", 0),
            "efficiency": existing.get("efficiency", 0),
            "security": existing.get("security", 0),
            "skills": existing.get("skills", 0),
            "ux": existing.get("ux", 0),
            "foundationScore": existing.get("foundationScore", 0),
            "subjectScore": existing.get("subjectScore", 0),
            "subjectBreakdown": existing.get("subjectBreakdown", {}),
        },
        "tasksAccepted": len(existing.get("taskResults", []) or []),
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
