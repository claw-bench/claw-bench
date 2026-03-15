"""Task loading and TOML parsing for claw-bench tasks."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import tomli
from pydantic import BaseModel, Field


class TaskConfig(BaseModel):
    """Schema for a single benchmark task defined in task.toml."""

    id: str
    domain: str
    level: str = Field(pattern=r"^L[1-4]$")
    title: str
    description: str
    timeout: int = Field(default=300, description="Timeout in seconds")
    capabilities: list[str] = Field(default_factory=list)
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

    # Inject the directory name as the task id when not explicitly set.
    raw.setdefault("id", task_dir.name)
    return TaskConfig(**raw)


def load_all_tasks(
    tasks_root: Path,
    domain: Optional[str] = None,
    level: Optional[str] = None,
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
            if task_ids and task.id not in task_ids:
                continue
            tasks.append(task)
            task_dirs[task.id] = task_dir

    return tasks, task_dirs
