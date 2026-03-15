"""Test tier selection for quick / track / comprehensive evaluation."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Sequence

from claw_bench.core.task_loader import TaskConfig

# Tier definitions
TIER_QUICK = "quick"
TIER_TRACK = "track"
TIER_COMPREHENSIVE = "comprehensive"

VALID_TIERS = (TIER_QUICK, TIER_TRACK, TIER_COMPREHENSIVE)

# Default runs-per-task for each tier
TIER_DEFAULTS: dict[str, dict] = {
    TIER_QUICK: {"runs": 1, "timeout": 600},
    TIER_TRACK: {"runs": 3, "timeout": 600},
    TIER_COMPREHENSIVE: {"runs": 5, "timeout": 600},
}

QUICK_TASK_IDS = [
    # L1 Easy (4 tasks) — baseline: any competent agent should pass
    "file-002",   # file-operations: CSV to JSON (8 checks)
    "code-002",   # code-assistance: palindrome checker (5 checks)
    "eml-001",    # email: parse headers (4 checks)
    "data-002",   # data-analysis: sort/filter CSV (6 checks)
    # L2 Medium (6 tasks) — standard agent tasks
    "cal-006",    # calendar: recurring meeting (4 checks)
    "doc-004",    # document-editing: find-replace patterns (11 checks)
    "sys-004",    # system-admin: log analysis (15 checks)
    "comm-004",   # communication: chat analysis (10 checks)
    "sec-004",    # security: SQL injection detection (8 checks)
    "wfl-003",    # workflow: multi-step pipeline (11 checks)
    # L3 Hard (3 tasks) — challenges for strong agents
    "web-006",    # web-browsing: accessibility audit (13 checks)
    "mem-005",    # memory: long doc summarization (18 checks)
    "xdom-001",   # cross-domain: email to calendar (10 checks)
    # L4 Expert (2 tasks) — only the best agents pass
    "code-014",   # code-assistance: multi-file refactoring (varies)
    "mm-005",     # multimodal: multi-format data pipeline (15 checks)
]


def _load_curated_quick_tasks() -> list[str] | None:
    """Load curated quick-task IDs from config/quick_tasks.yaml if it exists."""
    config_path = (
        Path(__file__).resolve().parent.parent.parent.parent
        / "config"
        / "quick_tasks.yaml"
    )
    if not config_path.exists():
        return None
    try:
        import yaml

        with open(config_path) as f:
            data = yaml.safe_load(f)
        return data.get("tasks", []) if data else None
    except Exception:
        return None


def select_quick_tasks(all_tasks: Sequence[TaskConfig]) -> list[TaskConfig]:
    """Select 15 curated tasks for the quick smoke test.

    Uses the hardcoded QUICK_TASK_IDS list (embedded in code, not external file).
    Falls back to one-per-domain algorithmic selection if curated IDs don't match.
    """
    id_set = set(QUICK_TASK_IDS)
    selected = [t for t in all_tasks if t.id in id_set]
    if len(selected) >= 10:
        return sorted(selected, key=lambda t: t.id)

    curated_ids = _load_curated_quick_tasks()
    if curated_ids:
        yaml_set = set(curated_ids)
        yaml_selected = [t for t in all_tasks if t.id in yaml_set]
        if yaml_selected:
            return sorted(yaml_selected, key=lambda t: t.id)

    by_domain: dict[str, list[TaskConfig]] = defaultdict(list)
    for t in all_tasks:
        by_domain[t.domain].append(t)

    picked: list[TaskConfig] = []
    for domain in sorted(by_domain):
        tasks = sorted(by_domain[domain], key=lambda t: t.id)
        l1 = [t for t in tasks if t.level == "L1"]
        if l1:
            picked.append(l1[0])
        else:
            l2 = [t for t in tasks if t.level == "L2"]
            if l2:
                picked.append(l2[0])
            elif tasks:
                picked.append(tasks[0])

    return picked


def select_track_tasks(
    all_tasks: Sequence[TaskConfig],
    domain: str,
) -> list[TaskConfig]:
    """Select all tasks in a single domain for a deep-dive evaluation."""
    return sorted(
        [t for t in all_tasks if t.domain == domain],
        key=lambda t: t.id,
    )
