#!/usr/bin/env python3
"""Batch validation script for all claw-bench tasks.

Walks all task directories, validates task.toml against the schema, checks
that required files exist, and optionally runs oracle solutions and verifiers.

Usage::

    python scripts/validate_all_tasks.py
    python scripts/validate_all_tasks.py --run-oracle
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import tomli

# Project root is one level up from the scripts/ directory
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_TASKS_ROOT = _PROJECT_ROOT / "tasks"
_SCHEMA_PATH = _TASKS_ROOT / "_schema" / "task.schema.json"


def load_schema() -> dict:
    """Load the task JSON schema."""
    with open(_SCHEMA_PATH) as fh:
        return json.load(fh)


def validate_toml_against_schema(data: dict, schema: dict) -> list[str]:
    """Perform basic validation of task data against the JSON schema.

    This is a lightweight check that does not require jsonschema; it validates
    required fields, types, and enum values from the schema.
    """
    errors: list[str] = []

    # Check required fields
    for field in schema.get("required", []):
        if field not in data:
            errors.append(f"Missing required field: {field}")

    props = schema.get("properties", {})
    for key, value in data.items():
        if key not in props:
            errors.append(f"Unknown field: {key}")
            continue

        prop_schema = props[key]
        expected_type = prop_schema.get("type")

        # Type checking
        type_map = {
            "string": str,
            "integer": int,
            "boolean": bool,
            "array": list,
        }
        if expected_type in type_map and not isinstance(value, type_map[expected_type]):
            errors.append(
                f"Field '{key}' should be {expected_type}, got {type(value).__name__}"
            )

        # Enum checking (top-level)
        if "enum" in prop_schema and value not in prop_schema["enum"]:
            errors.append(
                f"Field '{key}' value '{value}' not in allowed values: {prop_schema['enum']}"
            )

        # Array item validation
        if expected_type == "array" and isinstance(value, list):
            items_schema = prop_schema.get("items", {})
            item_enum = items_schema.get("enum")
            if item_enum:
                for i, item in enumerate(value):
                    if item not in item_enum:
                        errors.append(
                            f"Field '{key}[{i}]' value '{item}' not in allowed values: {item_enum}"
                        )
            min_items = prop_schema.get("minItems")
            if min_items is not None and len(value) < min_items:
                errors.append(
                    f"Field '{key}' has {len(value)} items, minimum is {min_items}"
                )

    return errors


def validate_task_dir(task_dir: Path, schema: dict) -> list[str]:
    """Validate a single task directory. Returns a list of error strings."""
    errors: list[str] = []

    # Check task.toml exists and is valid
    toml_path = task_dir / "task.toml"
    if not toml_path.exists():
        errors.append("task.toml not found")
        return errors

    try:
        with open(toml_path, "rb") as fh:
            data = tomli.load(fh)
    except Exception as exc:
        errors.append(f"task.toml parse error: {exc}")
        return errors

    errors.extend(validate_toml_against_schema(data, schema))

    # Check required files
    required_files = [
        "instruction.md",
        "verifier/test_output.py",
    ]
    for rel_path in required_files:
        if not (task_dir / rel_path).exists():
            errors.append(f"Missing required file: {rel_path}")

    return errors


def run_oracle(task_dir: Path) -> tuple[bool, str]:
    """Run the oracle solution and verifier for a task.

    Returns (success, details).
    """
    solution_sh = task_dir / "solution" / "solve.sh"
    if not solution_sh.exists():
        return False, "No oracle solution (solution/solve.sh) found"

    workspace = task_dir / "workspace"
    workspace.mkdir(parents=True, exist_ok=True)

    # Copy data files if present
    data_dir = task_dir / "environment" / "data"
    if data_dir.exists():
        import shutil

        for f in data_dir.iterdir():
            dest = workspace / f.name
            if f.is_file():
                shutil.copy2(f, dest)

    # Run setup if present
    setup_sh = task_dir / "environment" / "setup.sh"
    if setup_sh.exists():
        subprocess.run(
            ["bash", str(setup_sh)],
            cwd=str(task_dir),
            capture_output=True,
            timeout=30,
        )

    # Run oracle solution
    result = subprocess.run(
        ["bash", str(solution_sh)],
        cwd=str(workspace),
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode != 0:
        return False, f"Oracle solution failed (exit {result.returncode}): {result.stderr}"

    # Run verifier
    test_file = task_dir / "verifier" / "test_output.py"
    if not test_file.exists():
        return False, "No verifier found"

    tasks_root = task_dir.parent.parent
    verify_result = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            str(test_file),
            f"--workspace={workspace}",
            f"--rootdir={tasks_root}",
            "-q", "--tb=short", "--no-header",
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )

    if verify_result.returncode == 0:
        return True, "Oracle passed verification"
    else:
        return False, f"Oracle failed verification:\n{verify_result.stdout}\n{verify_result.stderr}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate all claw-bench tasks")
    parser.add_argument(
        "--run-oracle",
        action="store_true",
        help="Run oracle solutions and verifiers for each task",
    )
    args = parser.parse_args()

    schema = load_schema()
    results: list[dict] = []
    any_failed = False

    for domain_dir in sorted(_TASKS_ROOT.iterdir()):
        if not domain_dir.is_dir() or domain_dir.name.startswith(("_", ".")):
            continue
        for task_dir in sorted(domain_dir.iterdir()):
            if not task_dir.is_dir() or task_dir.name.startswith("."):
                continue

            task_id = task_dir.name
            errors = validate_task_dir(task_dir, schema)

            oracle_ok: bool | None = None
            oracle_detail = ""
            if args.run_oracle and not errors:
                oracle_ok, oracle_detail = run_oracle(task_dir)

            status = "PASS" if not errors else "FAIL"
            if errors:
                any_failed = True
            if oracle_ok is False:
                status = "FAIL"
                any_failed = True

            results.append({
                "task_id": task_id,
                "domain": domain_dir.name,
                "status": status,
                "errors": errors,
                "oracle_ok": oracle_ok,
                "oracle_detail": oracle_detail,
            })

    # Print summary table
    print(f"\n{'Task ID':<40} {'Domain':<20} {'Status':<8} {'Details'}")
    print("-" * 100)
    for r in results:
        detail = "; ".join(r["errors"]) if r["errors"] else ""
        if r["oracle_ok"] is not None:
            oracle_str = "oracle=PASS" if r["oracle_ok"] else "oracle=FAIL"
            detail = f"{detail}; {oracle_str}" if detail else oracle_str
            if not r["oracle_ok"] and r["oracle_detail"]:
                detail += f" ({r['oracle_detail'][:60]})"
        print(f"{r['task_id']:<40} {r['domain']:<20} {r['status']:<8} {detail}")

    total = len(results)
    passed = sum(1 for r in results if r["status"] == "PASS")
    print(f"\n{passed}/{total} tasks passed validation.")

    if any_failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
