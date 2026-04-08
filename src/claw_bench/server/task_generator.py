"""LLM-powered task generation from expert proposals.

Provides API endpoints that:
1. Accept an expert proposal and call an LLM to generate complete task files
2. Store generated tasks for admin review
3. Allow admins to approve/reject/edit generated tasks
4. Write approved tasks to the tasks/ directory

This replaces the GitHub Actions workflow with an in-app backend solution.
"""

from __future__ import annotations

import json
import logging
import os
import re
import textwrap
import time
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Header, BackgroundTasks
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin", tags=["task-generator"])

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
_DATA_DIR = _PROJECT_ROOT / "data"
_TASKS_DIR = _PROJECT_ROOT / "tasks"
_GENERATED_DIR = _DATA_DIR / "generated-tasks"
_PROPOSALS_DIR = _DATA_DIR / "expert-proposals"

for d in [_GENERATED_DIR, _PROPOSALS_DIR]:
    try:
        d.mkdir(parents=True, exist_ok=True)
    except OSError:
        pass

# ---------------------------------------------------------------------------
# Auth (reuse admin token verification)
# ---------------------------------------------------------------------------

_ADMIN_FILE = _DATA_DIR / ".admin_token"


def _get_admin_token() -> str:
    if _ADMIN_FILE.exists():
        return _ADMIN_FILE.read_text().strip()
    import secrets
    token = secrets.token_urlsafe(32)
    _ADMIN_FILE.write_text(token)
    return token


def verify_admin(authorization: str = Header(...)) -> str:
    import secrets as _secrets
    token = authorization.replace("Bearer ", "")
    if not _secrets.compare_digest(token, _get_admin_token()):
        raise HTTPException(401, "Invalid admin token")
    return token


_EXPERT_TOKEN_FILE = _DATA_DIR / ".expert_token"


def _get_expert_token() -> str:
    if _EXPERT_TOKEN_FILE.exists():
        return _EXPERT_TOKEN_FILE.read_text().strip()
    import secrets
    token = secrets.token_urlsafe(32)
    _EXPERT_TOKEN_FILE.write_text(token)
    return token


def verify_expert(authorization: str = Header(...)) -> str:
    import secrets as _secrets
    token = authorization.replace("Bearer ", "")
    if not _secrets.compare_digest(token, _get_expert_token()):
        raise HTTPException(401, "Invalid expert token")
    return token


# ---------------------------------------------------------------------------
# Domain constants
# ---------------------------------------------------------------------------

DOMAIN_DIR_MAP = {
    "computer-science": "computer-science",
    "mathematics": "mathematics",
    "physics-engineering": "physics-engineering",
    "biology-chemistry": "biology-chemistry",
    "financial-analysis": "financial-analysis",
    "accounting": "accounting",
    "marketing": "marketing",
    "contract-review": "contract-review",
    "legal-research": "legal-research",
    "clinical-data": "clinical-data",
    "medical-research": "medical-research",
    "sociology": "sociology",
    "education": "education",
    "multi-agent": "multi-agent",
}

DOMAIN_PREFIX_MAP = {
    "computer-science": "cs",
    "mathematics": "math",
    "physics-engineering": "phys",
    "biology-chemistry": "bio",
    "financial-analysis": "fin",
    "accounting": "acct",
    "marketing": "mkt",
    "contract-review": "law",
    "legal-research": "lres",
    "clinical-data": "clin",
    "medical-research": "mres",
    "sociology": "soc",
    "education": "edu",
    "multi-agent": "mag",
}

DEFAULT_MODEL = os.environ.get("TASK_GEN_MODEL", "gpt-4.1-mini")

AVAILABLE_MODELS = [
    {"id": "deepseek/deepseek-chat-v3-0324", "label": "DeepSeek V3 0324", "provider": "DeepSeek"},
    {"id": "anthropic/claude-sonnet-4.6", "label": "Claude Sonnet 4.6", "provider": "Anthropic"},
    {"id": "anthropic/claude-opus-4.6", "label": "Claude Opus 4.6", "provider": "Anthropic"},
    {"id": "anthropic/claude-sonnet-4.5", "label": "Claude Sonnet 4.5", "provider": "Anthropic"},
    {"id": "openai/gpt-5.2", "label": "GPT-5.2", "provider": "OpenAI"},
    {"id": "openai/gpt-5.1", "label": "GPT-5.1", "provider": "OpenAI"},
    {"id": "openai/gpt-4.1", "label": "GPT-4.1", "provider": "OpenAI"},
    {"id": "openai/gpt-4.1-mini", "label": "GPT-4.1 Mini", "provider": "OpenAI"},
    {"id": "openai/gpt-4o", "label": "GPT-4o", "provider": "OpenAI"},
    {"id": "google/gemini-3.1-pro-preview", "label": "Gemini 3.1 Pro", "provider": "Google"},
    {"id": "google/gemini-3-pro-preview", "label": "Gemini 3 Pro", "provider": "Google"},
    {"id": "google/gemini-3-flash-preview", "label": "Gemini 3 Flash", "provider": "Google"},
    {"id": "google/gemini-2.5-pro", "label": "Gemini 2.5 Pro", "provider": "Google"},
]

_MODEL_CONFIG_FILE = _DATA_DIR / "config" / "task_gen_model.json"


def _get_active_model() -> str:
    if _MODEL_CONFIG_FILE.exists():
        try:
            data = json.loads(_MODEL_CONFIG_FILE.read_text())
            return data.get("model", DEFAULT_MODEL)
        except (json.JSONDecodeError, OSError):
            pass
    return DEFAULT_MODEL


def _set_active_model(model_id: str) -> None:
    _MODEL_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    _MODEL_CONFIG_FILE.write_text(json.dumps({"model": model_id}, indent=2))


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class GenerateRequest(BaseModel):
    """Request to generate a task from a proposal."""
    proposalId: str


class GeneratedFile(BaseModel):
    """A single generated file."""
    path: str
    content: str


class GeneratedTask(BaseModel):
    """A complete generated task ready for review."""
    taskId: str
    proposalId: str
    domain: str
    taskTitle: str
    difficulty: str
    status: str  # "generating", "ready", "approved", "rejected"
    files: Dict[str, str]  # relative_path -> content
    generatedAt: str
    error: Optional[str] = None


class ApproveRequest(BaseModel):
    """Request to approve a generated task, optionally with edits."""
    files: Optional[Dict[str, str]] = None  # optional edited files


# ---------------------------------------------------------------------------
# Task ID generation
# ---------------------------------------------------------------------------


def _generate_task_id(domain: str) -> str:
    prefix = DOMAIN_PREFIX_MAP.get(domain, "task")
    domain_dir = _TASKS_DIR / DOMAIN_DIR_MAP.get(domain, domain)

    existing_ids: list[int] = []
    if domain_dir.exists():
        for d in domain_dir.iterdir():
            if d.is_dir():
                match = re.search(r"-(\d{3})", d.name)
                if match:
                    existing_ids.append(int(match.group(1)))

    # Also check generated tasks to avoid ID collision
    for f in _GENERATED_DIR.glob("*.json"):
        try:
            data = json.loads(f.read_text())
            if data.get("domain") == domain and data.get("status") != "rejected":
                tid = data.get("taskId", "")
                match = re.search(r"-(\d{3})", tid)
                if match:
                    existing_ids.append(int(match.group(1)))
        except (json.JSONDecodeError, OSError):
            continue

    next_num = max(existing_ids, default=0) + 1
    return f"{prefix}-{next_num:03d}"


def _slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text[:60].strip("-")


# ---------------------------------------------------------------------------
# LLM interaction
# ---------------------------------------------------------------------------


def _call_llm(prompt: str, model: str | None = None) -> str:
    """Call the LLM via OpenAI-compatible API."""
    if model is None:
        model = _get_active_model()

    try:
        from openai import OpenAI
    except ImportError:
        raise HTTPException(500, "openai package not installed. Run: pip install openai")

    client = OpenAI()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a benchmark task engineer for Claw-Bench, an AI Agent evaluation framework. "
                    "You generate complete, runnable benchmark tasks from expert proposals. "
                    "Your output must be precise, executable, and follow the exact format specified. "
                    "All tasks MUST test agent ACTION-TAKING capabilities (file operations, API calls, "
                    "database queries, script execution, environment configuration, web navigation, "
                    "git operations, etc.), NOT just knowledge or Q&A. "
                    "The agent must interact with the system environment to complete the task."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_tokens=8000,
    )
    return response.choices[0].message.content or ""


def _build_generation_prompt(proposal: dict, task_id: str, task_dir_name: str, difficulty: str) -> str:
    actions_str = ", ".join(proposal.get("requiredActions", []))

    return textwrap.dedent(f"""\
    Generate a complete Claw-Bench benchmark task from the following expert proposal.

    ## Expert Proposal
    - **Domain**: {proposal.get("domain", "")}
    - **Title**: {proposal.get("taskTitle", "")}
    - **Difficulty**: {difficulty}
    - **Real-world Context**: {proposal.get("context", "")}
    - **Agent Instruction**: {proposal.get("instruction", "")}
    - **Required Agent Actions**: {actions_str}
    - **Success Criteria**: {proposal.get("successCriteria", "")}
    - **Data Requirements**: {proposal.get("dataRequirements", "")}

    ## Task ID and Directory
    - Task ID: `{task_id}`
    - Directory name: `{task_dir_name}`

    ## Required Output

    Generate the following files. Output each file between markers like:
    ```
    === FILE: <filename> ===
    <content>
    === END FILE ===
    ```

    ### 1. task.toml
    Follow this exact format:
    ```toml
    id = "{task_id}"
    title = "<title>"
    track = "subject-matter"
    domain = "{proposal.get("domain", "")}"
    level = "{difficulty}"
    description = "<one-line description>"
    timeout = <seconds, 120-600 based on complexity>
    capabilities = [<list of capability strings>]
    required_actions = [{', '.join(f'"{a}"' for a in proposal.get("requiredActions", []))}]
    skills_allowed = true
    tags = [<relevant tags>]
    capability_types = [<from: "reasoning", "tool-use", "memory", "multimodal", "collaboration">]
    ```

    ### 2. instruction.md
    Write a clear, detailed instruction for the AI Agent. Include:
    - A title (# Task: ...)
    - Context about what the agent needs to do
    - Step-by-step requirements
    - Expected output format and location
    - Any constraints or important notes
    The instruction MUST require the agent to perform CONCRETE ACTIONS (run scripts, modify files,
    call APIs, query databases, configure environments, navigate web pages, use git, etc.),
    not just answer questions or produce text.

    ### 3. environment/setup.sh
    A bash script that:
    - Creates the workspace directory
    - Generates or copies any required test data files (synthetic/mock data)
    - Installs any required packages (pip install, apt-get, etc.)
    - Starts any mock services if needed (e.g., a simple Flask API server, a local SQLite DB)
    - Must be idempotent and use `set -euo pipefail`
    IMPORTANT: Generate realistic synthetic test data inline in the script.
    Do NOT reference external files that don't exist.

    ### 4. environment/data/ files
    If the task needs input data files (CSV, JSON, SQL, etc.), generate them.
    Output each data file as a separate FILE block.
    Make the data realistic but synthetic (no real PII).

    ### 5. verifier/test_output.py
    A pytest-based verification script that:
    - Uses `@pytest.fixture` for workspace path
    - Tests that the agent produced correct output files
    - Tests that output content matches expected criteria
    - Tests SYSTEM STATE changes (files moved/created, databases updated, services configured, etc.)
    - Tests that required actions were actually performed (not just hardcoded answers)
    - Uses `@pytest.mark.weight(N)` for scoring (higher N = more important)
    - Includes at least 5 test functions
    - Checks for the specific success criteria from the expert

    The verifier MUST check:
    a) Output file existence and format
    b) Output content correctness (specific values, structures)
    c) System state changes (files created/moved, DB records, env changes, etc.)
    d) That the agent didn't just hardcode answers but actually processed data

    ### 6. verifier/expected/ files (optional)
    If there are expected output files for comparison, generate them.

    ### 7. solution/solve.sh
    An oracle solution script that correctly completes the task.
    This proves the task is solvable and serves as a reference.
    Must use `set -euo pipefail` and accept workspace path as $1.

    ## Important Rules
    - All generated data must be SYNTHETIC and realistic
    - The task MUST require the agent to EXECUTE actions, not just produce text
    - The verifier must check both outputs AND system state changes
    - Scripts must be self-contained and runnable in a clean Ubuntu environment
    - Use Python 3.11+ compatible code
    """)


def _parse_llm_output(raw: str, task_id: str, task_dir_name: str, domain: str) -> Dict[str, str]:
    """Parse LLM output into a dict of relative_path -> content."""
    files: Dict[str, str] = {}
    domain_dir = DOMAIN_DIR_MAP.get(domain, domain)
    base = f"tasks/{domain_dir}/{task_dir_name}"

    pattern = r"===\s*FILE:\s*(.+?)\s*===\s*\n(.*?)===\s*END FILE\s*==="
    matches = re.findall(pattern, raw, re.DOTALL)

    for filename, content in matches:
        filename = filename.strip()
        content = content.strip()

        # Remove markdown code fences if present
        content = re.sub(r"^```\w*\n", "", content)
        content = re.sub(r"\n```$", "", content)

        if filename == "task.toml":
            files[f"{base}/task.toml"] = content + "\n"
        elif filename == "instruction.md":
            files[f"{base}/instruction.md"] = content + "\n"
        elif filename in ("setup.sh", "environment/setup.sh"):
            files[f"{base}/environment/setup.sh"] = content + "\n"
        elif filename in ("test_output.py", "verifier/test_output.py"):
            files[f"{base}/verifier/test_output.py"] = content + "\n"
        elif filename in ("solve.sh", "solution/solve.sh"):
            files[f"{base}/solution/solve.sh"] = content + "\n"
        elif filename.startswith("environment/data/") or filename.startswith("data/"):
            clean = filename if filename.startswith("environment/") else f"environment/{filename}"
            files[f"{base}/{clean}"] = content + "\n"
        elif filename.startswith("verifier/expected/") or filename.startswith("expected/"):
            clean = filename if filename.startswith("verifier/") else f"verifier/{filename}"
            files[f"{base}/{clean}"] = content + "\n"
        else:
            files[f"{base}/environment/data/{filename}"] = content + "\n"

    # Ensure minimum required files with fallbacks
    required = {
        f"{base}/task.toml": None,
        f"{base}/instruction.md": None,
        f"{base}/environment/setup.sh": None,
        f"{base}/verifier/test_output.py": None,
        f"{base}/solution/solve.sh": None,
    }
    for path in required:
        if path not in files:
            files[path] = _generate_fallback(path, task_id, domain)

    return files


def _generate_fallback(path: str, task_id: str, domain: str) -> str:
    """Generate minimal fallback content for missing files."""
    if path.endswith("task.toml"):
        return textwrap.dedent(f"""\
        id = "{task_id}"
        title = "Auto-generated task"
        track = "subject-matter"
        domain = "{domain}"
        level = "L2"
        description = "Auto-generated task — needs manual review"
        timeout = 300
        capabilities = ["script-execution", "file-write"]
        required_actions = ["script-execution", "file-write"]
        skills_allowed = true
        tags = ["auto-generated", "{domain}"]
        capability_types = ["tool-use", "reasoning"]
        """)
    elif path.endswith("instruction.md"):
        return "# Task\n\nAuto-generated instruction — needs manual review.\n"
    elif path.endswith("setup.sh"):
        return textwrap.dedent("""\
        #!/usr/bin/env bash
        set -euo pipefail
        TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
        WORKSPACE="${1:-$TASK_DIR/workspace}"
        mkdir -p "$WORKSPACE"
        echo "Workspace ready at $WORKSPACE"
        """)
    elif path.endswith("test_output.py"):
        return textwrap.dedent("""\
        \"\"\"Auto-generated verifier — needs manual review.\"\"\"
        import pytest
        from pathlib import Path

        @pytest.fixture
        def workspace(tmp_path):
            return tmp_path

        @pytest.mark.weight(3)
        def test_output_exists(workspace):
            files = list(workspace.iterdir())
            assert len(files) > 0, "No output files found"
        """)
    elif path.endswith("solve.sh"):
        return textwrap.dedent("""\
        #!/usr/bin/env bash
        set -euo pipefail
        WORKSPACE="${1:-workspace}"
        mkdir -p "$WORKSPACE"
        echo "TODO: Implement oracle solution" > "$WORKSPACE/README.md"
        """)
    return "# Auto-generated — needs review\n"


# ---------------------------------------------------------------------------
# Background generation
# ---------------------------------------------------------------------------


def _run_generation(proposal_data: dict, gen_id: str):
    """Run LLM generation in background thread."""
    gen_file = _GENERATED_DIR / f"{gen_id}.json"

    try:
        domain = proposal_data.get("domain", "computer-science")
        task_id = _generate_task_id(domain)
        slug = _slugify(proposal_data.get("taskTitle", "untitled"))
        task_dir_name = f"{task_id}-{slug}"
        difficulty = proposal_data.get("difficulty", "L2")

        prompt = _build_generation_prompt(proposal_data, task_id, task_dir_name, difficulty)
        raw_output = _call_llm(prompt)
        files = _parse_llm_output(raw_output, task_id, task_dir_name, domain)

        result = {
            "taskId": task_id,
            "taskDirName": task_dir_name,
            "proposalId": proposal_data.get("_proposalId", ""),
            "domain": domain,
            "taskTitle": proposal_data.get("taskTitle", ""),
            "difficulty": difficulty,
            "status": "ready",
            "files": files,
            "generatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "error": None,
        }
        gen_file.write_text(json.dumps(result, indent=2, ensure_ascii=False))

        # Update proposal status
        proposal_id = proposal_data.get("_proposalId", "")
        if proposal_id:
            pf = _PROPOSALS_DIR / f"{proposal_id}.json"
            if pf.exists():
                pd = json.loads(pf.read_text())
                pd["_status"] = "generated"
                pd["_generatedTaskId"] = gen_id
                pf.write_text(json.dumps(pd, indent=2, ensure_ascii=False))

        logger.info("Task generation completed: %s -> %s", gen_id, task_id)

    except Exception as e:
        logger.error("Task generation failed for %s: %s", gen_id, str(e))
        result = {
            "taskId": "",
            "taskDirName": "",
            "proposalId": proposal_data.get("_proposalId", ""),
            "domain": proposal_data.get("domain", ""),
            "taskTitle": proposal_data.get("taskTitle", ""),
            "difficulty": proposal_data.get("difficulty", ""),
            "status": "error",
            "files": {},
            "generatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "error": str(e),
        }
        gen_file.write_text(json.dumps(result, indent=2, ensure_ascii=False))


# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------


@router.get("/task-gen-models")
async def get_task_gen_models(_: str = Depends(verify_admin)):
    """Return available models and the currently active one."""
    return {
        "models": AVAILABLE_MODELS,
        "active": _get_active_model(),
    }


@router.put("/task-gen-models")
async def set_task_gen_model(
    body: dict,
    _: str = Depends(verify_admin),
):
    """Set the active model for task generation."""
    model_id = body.get("model", "")
    valid_ids = {m["id"] for m in AVAILABLE_MODELS}
    if model_id not in valid_ids:
        raise HTTPException(400, f"Invalid model: {model_id}")
    _set_active_model(model_id)
    logger.info("Task generation model changed to: %s", model_id)
    return {"status": "ok", "active": model_id}


@router.post("/generate-task")
async def generate_task_from_proposal(
    req: GenerateRequest,
    background_tasks: BackgroundTasks,
    _: str = Depends(verify_admin),
):
    """Trigger LLM task generation from an existing proposal.

    The generation runs in the background. Poll GET /generated-tasks/{id}
    to check status.
    """
    proposal_file = _PROPOSALS_DIR / f"{req.proposalId}.json"
    if not proposal_file.exists():
        raise HTTPException(404, f"Proposal {req.proposalId} not found")

    proposal_data = json.loads(proposal_file.read_text())

    gen_id = f"gen-{int(time.time())}-{uuid4().hex[:6]}"

    # Write initial "generating" status
    initial = {
        "taskId": "",
        "taskDirName": "",
        "proposalId": req.proposalId,
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

    # Update proposal status
    proposal_data["_status"] = "generating"
    proposal_data["_generatedTaskId"] = gen_id
    proposal_file.write_text(json.dumps(proposal_data, indent=2, ensure_ascii=False))

    # Run generation in background
    background_tasks.add_task(_run_generation, proposal_data, gen_id)

    return {"status": "generating", "generatedTaskId": gen_id}


@router.get("/generated-tasks")
async def list_generated_tasks(_: str = Depends(verify_admin)):
    """List all generated tasks (for admin review dashboard)."""
    tasks = []
    for f in sorted(_GENERATED_DIR.glob("*.json"), reverse=True):
        try:
            data = json.loads(f.read_text())
            data["_id"] = f.stem
            # Don't send full file contents in list view
            data["fileCount"] = len(data.get("files", {}))
            data["filePaths"] = list(data.get("files", {}).keys())
            del data["files"]
            tasks.append(data)
        except (json.JSONDecodeError, OSError):
            continue
    return tasks


@router.get("/generated-tasks/{gen_id}")
async def get_generated_task(gen_id: str, _: str = Depends(verify_admin)):
    """Get a single generated task with full file contents (for review)."""
    filepath = _GENERATED_DIR / f"{gen_id}.json"
    if not filepath.exists():
        raise HTTPException(404, f"Generated task {gen_id} not found")
    data = json.loads(filepath.read_text())
    data["_id"] = gen_id
    return data


def _post_approve_sync():
    """Run after a task is approved: refresh VALID_TASK_IDS, domains.json, skill.md."""
    try:
        from claw_bench.server.submit_api import refresh_task_registry
        count = refresh_task_registry()
        logger.info("Post-approve sync: refreshed task registry (%d IDs), domains.json, and skill.md", count)
    except Exception as e:
        import traceback
        logger.error("Post-approve sync failed: %s\n%s", e, traceback.format_exc())


@router.post("/generated-tasks/{gen_id}/approve")
async def approve_generated_task(
    gen_id: str,
    req: Optional[ApproveRequest] = None,
    _: str = Depends(verify_admin),
):
    """Approve a generated task and write files to the tasks/ directory.

    Optionally accepts edited file contents to override the generated ones.
    """
    filepath = _GENERATED_DIR / f"{gen_id}.json"
    if not filepath.exists():
        raise HTTPException(404, f"Generated task {gen_id} not found")

    data = json.loads(filepath.read_text())
    if data.get("status") != "ready":
        raise HTTPException(400, f"Task is not ready for approval (status: {data.get('status')})")

    # Use edited files if provided, otherwise use generated files
    files = data.get("files", {})
    if req and req.files:
        files.update(req.files)

    # Write files to disk
    created = []
    for rel_path, content in files.items():
        full_path = _PROJECT_ROOT / rel_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)
        if full_path.suffix == ".sh":
            full_path.chmod(0o755)
        created.append(rel_path)
        logger.info("Written: %s", rel_path)

    # Update status
    data["status"] = "approved"
    data["approvedAt"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    filepath.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    # Update proposal status
    proposal_id = data.get("proposalId", "")
    if proposal_id:
        pf = _PROPOSALS_DIR / f"{proposal_id}.json"
        if pf.exists():
            pd = json.loads(pf.read_text())
            pd["_status"] = "approved"
            pf.write_text(json.dumps(pd, indent=2, ensure_ascii=False))

    # Auto-update docs, configs, and frontend after approval
    threading.Thread(target=_post_approve_sync, daemon=True).start()

    return {
        "status": "approved",
        "taskId": data.get("taskId"),
        "filesWritten": created,
    }


@router.post("/generated-tasks/{gen_id}/reject")
async def reject_generated_task(gen_id: str, _: str = Depends(verify_admin)):
    """Reject a generated task."""
    filepath = _GENERATED_DIR / f"{gen_id}.json"
    if not filepath.exists():
        raise HTTPException(404, f"Generated task {gen_id} not found")

    data = json.loads(filepath.read_text())
    data["status"] = "rejected"
    data["rejectedAt"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    filepath.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    # Update proposal status
    proposal_id = data.get("proposalId", "")
    if proposal_id:
        pf = _PROPOSALS_DIR / f"{proposal_id}.json"
        if pf.exists():
            pd = json.loads(pf.read_text())
            pd["_status"] = "rejected"
            pf.write_text(json.dumps(pd, indent=2, ensure_ascii=False))

    return {"status": "rejected", "generatedTaskId": gen_id}


@router.post("/generated-tasks/{gen_id}/regenerate")
async def regenerate_task(
    gen_id: str,
    background_tasks: BackgroundTasks,
    _: str = Depends(verify_admin),
):
    """Re-run LLM generation for a task (e.g., after rejection or error)."""
    filepath = _GENERATED_DIR / f"{gen_id}.json"
    if not filepath.exists():
        raise HTTPException(404, f"Generated task {gen_id} not found")

    data = json.loads(filepath.read_text())
    proposal_id = data.get("proposalId", "")
    if not proposal_id:
        raise HTTPException(400, "No linked proposal found")

    proposal_file = _PROPOSALS_DIR / f"{proposal_id}.json"
    if not proposal_file.exists():
        raise HTTPException(404, f"Proposal {proposal_id} not found")

    proposal_data = json.loads(proposal_file.read_text())

    # Reset status
    data["status"] = "generating"
    data["error"] = None
    data["files"] = {}
    filepath.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    background_tasks.add_task(_run_generation, proposal_data, gen_id)

    return {"status": "regenerating", "generatedTaskId": gen_id}


@router.delete("/generated-tasks/{gen_id}")
async def delete_generated_task(gen_id: str, _: str = Depends(verify_admin)):
    """Delete a generated task record."""
    filepath = _GENERATED_DIR / f"{gen_id}.json"
    if not filepath.exists():
        raise HTTPException(404, f"Generated task {gen_id} not found")
    filepath.unlink()
    return {"status": "deleted", "generatedTaskId": gen_id}
