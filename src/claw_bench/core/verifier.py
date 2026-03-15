"""Run pytest-based verifiers and parse their results."""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class VerificationResult:
    """Structured output from running a task verifier."""

    passed: bool
    details: str
    checks_total: int
    checks_passed: int


def verify_task(task_dir: Path, workspace: Path) -> VerificationResult:
    """Execute the pytest verifier for a task and return structured results.

    The verifier script is expected at ``<task_dir>/verifier/test_output.py``.
    The *workspace* path is injected via the ``--workspace`` pytest flag so
    that tests can locate generated artefacts.
    """
    test_file = task_dir / "verifier" / "test_output.py"
    if not test_file.exists():
        return VerificationResult(
            passed=False,
            details=f"Verifier not found: {test_file}",
            checks_total=0,
            checks_passed=0,
        )

    # Find the tasks root (parent of domain dirs) for conftest.py discovery
    tasks_root = task_dir.parent.parent

    cmd = [
        sys.executable,
        "-m",
        "pytest",
        str(test_file),
        f"--workspace={workspace}",
        f"--rootdir={tasks_root}",
        "-q",
        "--tb=short",
        "--no-header",
    ]

    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

    return _parse_stdout(proc.stdout)


def _parse_report(report_path: Path, fallback_stdout: str) -> VerificationResult:
    """Parse the JSON report produced by pytest-json-report.

    Falls back to basic stdout analysis when the JSON file is unavailable.
    """
    try:
        with open(report_path) as fh:
            data = json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError):
        return _parse_stdout(fallback_stdout)
    finally:
        try:
            report_path.unlink(missing_ok=True)
        except Exception:
            pass

    summary = data.get("summary", {})
    total = summary.get("total", 0)
    passed_count = summary.get("passed", 0)
    failed_count = summary.get("failed", 0)

    details_parts: list[str] = []
    for test in data.get("tests", []):
        outcome = test.get("outcome", "unknown")
        nodeid = test.get("nodeid", "?")
        details_parts.append(f"{outcome}: {nodeid}")

    return VerificationResult(
        passed=failed_count == 0 and total > 0,
        details="\n".join(details_parts),
        checks_total=total,
        checks_passed=passed_count,
    )


def _parse_stdout(stdout: str) -> VerificationResult:
    """Best-effort parse of pytest text output when JSON is unavailable."""
    lines = stdout.strip().splitlines()
    passed_count = 0
    failed_count = 0
    for line in lines:
        if " passed" in line:
            try:
                passed_count = int(line.split()[0])
            except (ValueError, IndexError):
                pass
        if " failed" in line:
            try:
                failed_count = int(line.split()[0])
            except (ValueError, IndexError):
                pass

    total = passed_count + failed_count
    return VerificationResult(
        passed=failed_count == 0 and total > 0,
        details=stdout,
        checks_total=total,
        checks_passed=passed_count,
    )
