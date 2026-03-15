"""Verifier for sys-008: Log Rotation Script."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def plan(workspace):
    """Load and return the rotation_plan.json contents."""
    path = workspace / "rotation_plan.json"
    assert path.exists(), "rotation_plan.json not found in workspace"
    return json.loads(path.read_text())


@pytest.fixture
def script(workspace):
    """Read and return the rotate.sh contents."""
    path = workspace / "rotate.sh"
    assert path.exists(), "rotate.sh not found in workspace"
    return path.read_text()


def test_rotation_plan_exists(workspace):
    """rotation_plan.json must exist in the workspace."""
    assert (workspace / "rotation_plan.json").exists()


def test_rotate_script_exists(workspace):
    """rotate.sh must exist in the workspace."""
    assert (workspace / "rotate.sh").exists()


def test_plan_total_files(plan):
    """Total files must equal 10."""
    assert plan["summary"]["total_files"] == 10


def test_plan_rotate_plus_skip_equals_total(plan):
    """to_rotate + to_skip must equal total_files."""
    total = plan["summary"]["to_rotate"] + plan["summary"]["to_skip"]
    assert total == plan["summary"]["total_files"]


def test_size_threshold_applied(plan):
    """Files >= 100MB must be marked for rotation."""
    large_files = {"application.log", "access.log", "debug.log", "mail.log", "kern.log"}
    rotate_names = {f["name"] for f in plan["files_to_rotate"]}
    for f in large_files:
        assert f in rotate_names, f"{f} (>=100MB) should be marked for rotation"


def test_age_threshold_applied(plan):
    """Files older than 7 days must be marked for rotation."""
    # error.log: 2024-03-02 (13 days), debug.log: 2024-02-28 (16 days),
    # mail.log: 2024-03-01 (14 days), daemon.log: 2024-03-05 (10 days)
    old_files = {"error.log", "debug.log", "mail.log", "daemon.log"}
    rotate_names = {f["name"] for f in plan["files_to_rotate"]}
    for f in old_files:
        assert f in rotate_names, f"{f} (>7 days old) should be marked for rotation"


def test_within_threshold_files_skipped(plan):
    """Files within both thresholds must be skipped."""
    # audit.log: 45.1MB, 1 day old; cron.log: 8.5MB, 0 days old
    skip_names = {f["name"] for f in plan["files_to_skip"]}
    assert "audit.log" in skip_names, "audit.log should be skipped (within thresholds)"
    assert "cron.log" in skip_names, "cron.log should be skipped (within thresholds)"


def test_rotation_reasons_correct(plan):
    """Rotation reasons must accurately reflect why each file needs rotation."""
    for entry in plan["files_to_rotate"]:
        assert entry["reason"] in ("size", "age", "both"), (
            f"Invalid reason '{entry['reason']}' for {entry['name']}"
        )
    # debug.log is both large (1024MB) and old (16 days)
    debug = [f for f in plan["files_to_rotate"] if f["name"] == "debug.log"]
    if debug:
        assert debug[0]["reason"] == "both", "debug.log should have reason 'both'"


def test_script_starts_with_shebang(script):
    """rotate.sh must start with a proper shebang line."""
    assert script.startswith("#!/"), "Script must start with shebang"
    assert "bash" in script.split("\n")[0], "Script must use bash"


def test_script_has_set_flags(script):
    """rotate.sh must include set -euo pipefail or similar safety flags."""
    assert "set -e" in script, "Script must include 'set -e' or similar"


def test_script_is_valid_bash(workspace, script):
    """rotate.sh must be syntactically valid bash."""
    import subprocess
    result = subprocess.run(
        ["bash", "-n", str(workspace / "rotate.sh")],
        capture_output=True, text=True
    )
    assert result.returncode == 0, f"Bash syntax check failed: {result.stderr}"


def test_script_references_rotated_files(plan, script):
    """rotate.sh must reference the files marked for rotation."""
    for entry in plan["files_to_rotate"]:
        assert entry["name"] in script, (
            f"rotate.sh does not reference {entry['name']}"
        )


def test_space_to_free(plan):
    """space_to_free_mb must be positive and reasonable."""
    assert plan["summary"]["space_to_free_mb"] > 0
    # Sum of sizes of rotated files should be substantial
    assert plan["summary"]["space_to_free_mb"] > 500, (
        "space_to_free_mb seems too low given the file sizes"
    )


def test_rules_documented(plan):
    """Rotation rules must be documented in the plan."""
    assert plan["rules"]["size_threshold_mb"] == 100
    assert plan["rules"]["age_threshold_days"] == 7
    assert plan["rules"]["max_rotations"] == 5
