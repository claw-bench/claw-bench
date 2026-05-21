"""Task loading and TOML parsing for claw-bench tasks."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import tomli
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Domain taxonomy
# ---------------------------------------------------------------------------

# Foundation domains (basic agent capabilities)
FOUNDATION_DOMAINS: set[str] = {
    "calendar", "code-assistance", "communication", "cross-domain",
    "data-analysis", "document-editing", "email", "file-operations",
    "memory", "multi-agent", "multimodal", "security", "system-admin",
    "web-browsing", "workflow-automation", "database", "debugging",
    "math-reasoning", "planning", "real-tools",
}

# Subject-matter domains (professional domain knowledge)
SUBJECT_MATTER_DOMAINS: set[str] = {
    "mathematics", "computer-science", "physics-engineering",
    "biology-chemistry", "financial-analysis", "accounting",
    "marketing", "contract-review", "legal-research",
    "clinical-data", "medical-research", "sociology", "education",
}

# Subject-matter domain -> high-level category mapping
SUBJECT_CATEGORY_MAP: dict[str, str] = {
    "mathematics": "STEM",
    "computer-science": "STEM",
    "physics-engineering": "STEM",
    "biology-chemistry": "STEM",
    "financial-analysis": "Business",
    "accounting": "Business",
    "marketing": "Business",
    "contract-review": "Law",
    "legal-research": "Law",
    "clinical-data": "Healthcare",
    "medical-research": "Healthcare",
    "sociology": "Humanities",
    "education": "Humanities",
}

# Subject-matter domain weights for scoring (must sum to 1.0)
SUBJECT_WEIGHTS: dict[str, float] = {
    "computer-science": 0.15,
    "mathematics": 0.10,
    "physics-engineering": 0.05,
    "biology-chemistry": 0.05,
    "financial-analysis": 0.15,
    "accounting": 0.10,
    "marketing": 0.05,
    "contract-review": 0.10,
    "legal-research": 0.05,
    "clinical-data": 0.05,
    "medical-research": 0.05,
    "sociology": 0.05,
    "education": 0.05,
}


# ---------------------------------------------------------------------------
# Task configuration model
# ---------------------------------------------------------------------------

class TaskConfig(BaseModel):
    """Schema for a single benchmark task defined in task.toml."""

    id: str
    track: str = Field(
        default="foundation",
        pattern=r"^(foundation|subject-matter)$",
        description="Evaluation track: foundation or subject-matter",
    )
    domain: str
    level: str = Field(pattern=r"^L[1-4]$")
    title: str
    description: str = ""
    timeout: int = Field(default=300, description="Timeout in seconds")
    capabilities: list[str] = Field(default_factory=list)
    required_actions: list[str] = Field(
        default_factory=list,
        description="Concrete agent actions required (e.g. api-call, script-execution)",
    )
    skills_allowed: bool = Field(default=True)
    capability_types: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


def load_task(task_dir: Path) -> TaskConfig:
    """Read task.toml from *task_dir* and return a validated TaskConfig.

    Raises ``FileNotFoundError`` if task.toml is missing and
    ``pydantic.ValidationError`` if the contents are invalid.
    """
    toml_path = task_dir / "task.toml"
    with open(toml_path, "rb") as fh:
        raw = tomli.load(fh)

    # Handle [task] section format: merge into top level
    if "task" in raw and isinstance(raw["task"], dict):
        task_section = raw.pop("task")
        for k, v in task_section.items():
            raw.setdefault(k, v)

    # Inject the directory name as the task id when not explicitly set.
    raw.setdefault("id", task_dir.name)

    # Auto-detect track from domain if not explicitly set.
    if "track" not in raw:
        domain = raw.get("domain", "")
        if domain in SUBJECT_MATTER_DOMAINS:
            raw["track"] = "subject-matter"
        else:
            raw["track"] = "foundation"

    return TaskConfig(**raw)


def load_all_tasks(
    tasks_root: Path,
    domain: Optional[str] = None,
    level: Optional[str] = None,
    track: Optional[str] = None,
    task_ids: Optional[list[str]] = None,
) -> tuple[list[TaskConfig], dict[str, Path]]:
    """Scan *tasks_root* for task directories and return matching tasks.

    The tasks directory is organized as::

        tasks/<domain>/<task-id>/task.toml

    Returns a tuple of (task_configs, task_dirs_map) where task_dirs_map
    maps task id -> directory path.
    """
    tasks: list[TaskConfig] = []
    task_dirs: dict[str, Path] = {}

    for domain_dir in sorted(tasks_root.iterdir()):
        if not domain_dir.is_dir() or domain_dir.name.startswith("_"):
            continue
        for task_dir in sorted(domain_dir.iterdir()):
            if not task_dir.is_dir():
                continue
            toml_path = task_dir / "task.toml"
            if not toml_path.exists():
                continue
            try:
                task = load_task(task_dir)
            except Exception:
                continue
            if domain and task.domain != domain:
                continue
            if level and task.level != level:
                continue
            if track and task.track != track:
                continue
            if task_ids and task.id not in task_ids:
                continue
            tasks.append(task)
            task_dirs[task.id] = task_dir

    return tasks, task_dirs
