#!/usr/bin/env python3
"""rotate-tasks.py - Quarterly task rotation for anti-contamination.

Rotates ~20% of tasks each quarter to prevent frameworks from overfitting
to a fixed task set. Archived tasks are moved to archive/<quarter>/ and
can be restored later.

Usage:
    python scripts/rotate-tasks.py --quarter 2026-Q2 [--dry-run]
    python scripts/rotate-tasks.py --quarter 2026-Q2 --percent 20
    python scripts/rotate-tasks.py --restore --quarter 2026-Q1
"""

from __future__ import annotations

import argparse
import json
import random
import shutil
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_TASKS_ROOT = _PROJECT_ROOT / "tasks"
_ARCHIVE_ROOT = _PROJECT_ROOT / "archive"


def discover_tasks() -> list[dict]:
    """Discover all tasks with their metadata."""
    tasks = []
    for domain_dir in sorted(_TASKS_ROOT.iterdir()):
        if not domain_dir.is_dir() or domain_dir.name.startswith(("_", ".")):
            continue
        for task_dir in sorted(domain_dir.iterdir()):
            if not task_dir.is_dir() or task_dir.name.startswith("."):
                continue
            toml_path = task_dir / "task.toml"
            if not toml_path.exists():
                continue
            try:
                import tomli
                with open(toml_path, "rb") as f:
                    config = tomli.load(f)
                tasks.append({
                    "id": config.get("id", task_dir.name),
                    "domain": config.get("domain", domain_dir.name),
                    "level": config.get("level", "L1"),
                    "dir": task_dir,
                    "domain_dir_name": domain_dir.name,
                })
            except Exception as e:
                print(f"  Warning: Could not parse {toml_path}: {e}")
    return tasks


def select_for_rotation(tasks: list[dict], percent: int, seed: int) -> list[dict]:
    """Select tasks for rotation, maintaining domain/level balance.

    Selects approximately `percent`% of tasks, ensuring at least one task
    from each domain is preserved (never rotate ALL tasks from a domain).
    """
    rng = random.Random(seed)
    num_to_rotate = max(1, int(len(tasks) * percent / 100))

    # Group by domain
    by_domain: dict[str, list[dict]] = {}
    for t in tasks:
        by_domain.setdefault(t["domain"], []).append(t)

    # Ensure we leave at least half of each domain's tasks
    eligible: list[dict] = []
    for domain, domain_tasks in by_domain.items():
        max_from_domain = max(1, len(domain_tasks) // 2)
        rng.shuffle(domain_tasks)
        eligible.extend(domain_tasks[:max_from_domain])

    rng.shuffle(eligible)
    return eligible[:num_to_rotate]


def archive_tasks(tasks_to_archive: list[dict], quarter: str, dry_run: bool) -> None:
    """Move selected tasks to the archive directory."""
    archive_dir = _ARCHIVE_ROOT / quarter
    if not dry_run:
        archive_dir.mkdir(parents=True, exist_ok=True)

    for task in tasks_to_archive:
        src = task["dir"]
        dest = archive_dir / task["domain_dir_name"] / src.name
        if dry_run:
            print(f"  [DRY RUN] Would archive: {task['id']} ({task['domain']}/{task['level']})")
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dest))
            print(f"  Archived: {task['id']} -> archive/{quarter}/{task['domain_dir_name']}/{src.name}")


def restore_tasks(quarter: str, dry_run: bool) -> None:
    """Restore archived tasks from a specific quarter."""
    archive_dir = _ARCHIVE_ROOT / quarter
    if not archive_dir.exists():
        print(f"No archive found for {quarter}")
        return

    restored = 0
    for domain_dir in sorted(archive_dir.iterdir()):
        if not domain_dir.is_dir():
            continue
        dest_domain = _TASKS_ROOT / domain_dir.name
        for task_dir in sorted(domain_dir.iterdir()):
            if not task_dir.is_dir():
                continue
            dest = dest_domain / task_dir.name
            if dry_run:
                print(f"  [DRY RUN] Would restore: {task_dir.name} -> {dest}")
            else:
                dest_domain.mkdir(parents=True, exist_ok=True)
                shutil.move(str(task_dir), str(dest))
                print(f"  Restored: {task_dir.name} -> {dest}")
            restored += 1

    if not dry_run and restored > 0:
        # Clean up empty archive directory
        shutil.rmtree(archive_dir, ignore_errors=True)

    print(f"\n{'Would restore' if dry_run else 'Restored'} {restored} tasks from {quarter}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Rotate benchmark tasks on a quarterly cadence."
    )
    parser.add_argument(
        "--quarter",
        required=True,
        help="Target quarter, e.g. 2026-Q2",
    )
    parser.add_argument(
        "--percent",
        type=int,
        default=20,
        help="Percentage of tasks to rotate (default: 20)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without applying them",
    )
    parser.add_argument(
        "--restore",
        action="store_true",
        help="Restore tasks from the specified quarter's archive",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducible selection (default: hash of quarter)",
    )
    args = parser.parse_args()

    print(f"Claw Bench Task Rotation — {args.quarter}")
    if args.dry_run:
        print("(dry-run mode — no changes will be applied)\n")

    if args.restore:
        restore_tasks(args.quarter, args.dry_run)
        return 0

    # Discovery
    tasks = discover_tasks()
    print(f"Found {len(tasks)} tasks across {len(set(t['domain'] for t in tasks))} domains\n")

    # Selection
    seed = args.seed if args.seed is not None else hash(args.quarter)
    to_rotate = select_for_rotation(tasks, args.percent, seed)
    print(f"Selected {len(to_rotate)} tasks for rotation ({args.percent}%):\n")

    # Summary by domain
    by_domain: dict[str, int] = {}
    for t in to_rotate:
        by_domain[t["domain"]] = by_domain.get(t["domain"], 0) + 1
    for domain, count in sorted(by_domain.items()):
        print(f"  {domain}: {count} tasks")
    print()

    # Archive
    archive_tasks(to_rotate, args.quarter, args.dry_run)

    # Final stats
    remaining = len(tasks) - len(to_rotate)
    print(f"\n{'Would have' if args.dry_run else 'Now'} {remaining} active tasks")
    print(f"Archived tasks can be restored with: python scripts/rotate-tasks.py --restore --quarter {args.quarter}")

    # Write manifest
    if not args.dry_run:
        manifest = {
            "quarter": args.quarter,
            "rotated_count": len(to_rotate),
            "rotated_tasks": [{"id": t["id"], "domain": t["domain"], "level": t["level"]} for t in to_rotate],
            "remaining_count": remaining,
        }
        manifest_path = _ARCHIVE_ROOT / args.quarter / "manifest.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest, indent=2))
        print(f"Manifest written to {manifest_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
