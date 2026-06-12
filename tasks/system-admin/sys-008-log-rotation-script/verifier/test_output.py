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


# ── Enhanced checks (auto-generated) ────────────────────────────────────────

@pytest.mark.weight(1)
def test_no_placeholder_values(workspace):
    """Output files must not contain placeholder/TODO markers."""
    placeholders = ["PLACEHOLDER", "CHANGEME"]
    for f in workspace.iterdir():
        if f.is_file() and f.suffix in (".json", ".csv", ".txt", ".md", ".py", ".yaml", ".yml", ".html", ".xml"):
            content = f.read_text(errors="replace")
            for p in placeholders:
                assert p not in content, f"Placeholder '{p}' found in {f.name}"

@pytest.mark.weight(2)
def test_no_empty_critical_fields(workspace):
    """JSON output must not have empty-string or null values in top-level fields."""
    import json
    path = workspace / "logs/log_manifest.json"
    if not path.exists():
        pytest.skip("output file not found")
    data = json.loads(path.read_text())
    items = data if isinstance(data, list) else [data]
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        non_empty = [
            v for v in item.values()
            if v is not None and (not isinstance(v, str) or v.strip() != "")
        ]
        assert non_empty, f"Item {i}: all fields are empty or null"

@pytest.mark.weight(1)
def test_encoding_valid(workspace):
    """All text output files must be valid UTF-8."""
    for f in workspace.iterdir():
        if f.is_file() and f.suffix in (".json", ".csv", ".txt", ".md", ".py", ".yaml", ".yml", ".html"):
            try:
                f.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                pytest.fail(f"{f.name} contains invalid UTF-8 encoding")

@pytest.mark.weight(1)
def test_consistent_key_naming(workspace):
    """JSON keys should use a consistent naming convention."""
    import json, re
    path = workspace / "logs/log_manifest.json"
    if not path.exists():
        pytest.skip("output file not found")
    data = json.loads(path.read_text())
    items = data if isinstance(data, list) else [data]
    all_keys = set()
    for item in items:
        if isinstance(item, dict):
            all_keys.update(item.keys())
    if len(all_keys) < 2:
        return
    snake = sum(1 for k in all_keys if re.match(r'^[a-z][a-z0-9_]*$', k))
    camel = sum(1 for k in all_keys if re.match(r'^[a-z][a-zA-Z0-9]*$', k) and not re.match(r'^[a-z][a-z0-9_]*$', k))
    pascal = sum(1 for k in all_keys if re.match(r'^[A-Z][a-zA-Z0-9]*$', k))
    dominant = max(snake, camel, pascal)
    classified = snake + camel + pascal
    if classified == 0:
        return
    consistency = dominant / classified
    assert consistency >= 0.7, f"Key naming inconsistent: {snake} snake, {camel} camel, {pascal} pascal out of {len(all_keys)} keys"

@pytest.mark.weight(1)
def test_no_duplicate_entries(workspace):
    """Output should not contain exact duplicate rows/objects."""
    import json
    path = workspace / "logs/log_manifest.json"
    if not path.exists():
        pytest.skip("output file not found")
    text = path.read_text().strip()
    if path.suffix == ".json":
        data = json.loads(text)
        if isinstance(data, list):
            serialized = [json.dumps(item, sort_keys=True) for item in data]
            dupes = len(serialized) - len(set(serialized))
            assert dupes == 0, f"Found {dupes} duplicate entries in {path.name}"
    elif path.suffix == ".csv":
        lines_list = text.splitlines()
        if len(lines_list) > 1:
            data_lines = lines_list[1:]
            dupes = len(data_lines) - len(set(data_lines))
            assert dupes == 0, f"Found {dupes} duplicate rows in {path.name}"

@pytest.mark.weight(1)
def test_no_extraneous_files(workspace):
    """Workspace should not contain debug/temp files."""
    bad_patterns = [".DS_Store", "Thumbs.db", ".bak", ".tmp"]
    for f in workspace.rglob("*"):
        if f.is_file():
            for pat in bad_patterns:
                assert pat not in f.name, f"Extraneous file found: {f.name}"

@pytest.mark.weight(1)
def test_output_not_excessively_large(workspace):
    """Output files should be reasonably sized (< 5MB each)."""
    for f in workspace.iterdir():
        if f.is_file() and f.suffix in (".json", ".csv", ".txt", ".md", ".py", ".yaml", ".yml", ".html"):
            size_mb = f.stat().st_size / (1024 * 1024)
            assert size_mb < 5, f"{f.name} is {size_mb:.1f}MB, exceeds 5MB limit"
