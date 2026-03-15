"""Comprehensive oracle solution verification for all tasks.

Run with: pytest tests/slow/ -m slow --timeout=600
Skipped by default in normal test runs.
"""

import shutil
import subprocess
from pathlib import Path

import pytest

TASKS_ROOT = Path(__file__).resolve().parents[2] / "tasks"


def discover_tasks():
    """Find all task directories with oracle solutions."""
    tasks = []
    for domain_dir in sorted(TASKS_ROOT.iterdir()):
        if not domain_dir.is_dir() or domain_dir.name.startswith(("_", ".")):
            continue
        for task_dir in sorted(domain_dir.iterdir()):
            if not task_dir.is_dir() or task_dir.name.startswith("."):
                continue
            if (task_dir / "solution" / "solve.sh").exists():
                tasks.append(task_dir)
    return tasks


@pytest.mark.slow
@pytest.mark.parametrize("task_dir", discover_tasks(), ids=lambda d: d.name)
def test_oracle_solution(task_dir, tmp_path):
    """Run oracle solution and verify it passes all checks."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    # Setup
    setup_sh = task_dir / "environment" / "setup.sh"
    if setup_sh.exists():
        subprocess.run(["bash", str(setup_sh), str(workspace)], check=True, timeout=30)

    # Copy data
    data_dir = task_dir / "environment" / "data"
    if data_dir.exists():
        for f in data_dir.iterdir():
            dest = workspace / f.name
            if f.is_file():
                shutil.copy2(f, dest)
            elif f.is_dir():
                shutil.copytree(f, dest, dirs_exist_ok=True)

    # Solve
    solve_sh = task_dir / "solution" / "solve.sh"
    result = subprocess.run(
        ["bash", str(solve_sh), str(workspace)], capture_output=True, timeout=60
    )
    assert result.returncode == 0, f"solve.sh failed: {result.stderr.decode()}"

    # Verify
    verifier = task_dir / "verifier" / "test_output.py"
    result = subprocess.run(
        [
            "python",
            "-m",
            "pytest",
            str(verifier),
            f"--workspace={workspace}",
            "-q",
            "--tb=short",
            f"--rootdir={TASKS_ROOT}",
            "-c",
            "/dev/null",
            "-p",
            "no:cacheprovider",
        ],
        capture_output=True,
        timeout=60,
        cwd=str(TASKS_ROOT),
    )
    assert result.returncode == 0, (
        f"Verifier failed:\n{result.stdout.decode()}\n{result.stderr.decode()}"
    )
