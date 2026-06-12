"""Verifier for wfl-008: Error Handling Workflow with Compensation."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def report(workspace):
    """Load the execution report."""
    path = workspace / "execution_report.json"
    assert path.exists(), "execution_report.json not found"
    return json.loads(path.read_text())


@pytest.fixture
def step_by_id(report):
    """Create a lookup dict by step ID."""
    return {s["id"]: s for s in report["steps"]}


def test_report_exists(workspace):
    """execution_report.json must exist."""
    assert (workspace / "execution_report.json").exists()


def test_all_steps_present(report):
    """All 8 steps must be in the report."""
    assert len(report["steps"]) == 8


def test_has_required_sections(report):
    """Report must have steps, compensations, workflow_status, summary."""
    assert "steps" in report
    assert "compensations" in report
    assert "workflow_status" in report
    assert "summary" in report


def test_step1_completed(step_by_id):
    """Step 1 (connect_db) should complete successfully then get compensated."""
    step = step_by_id["step_1"]
    assert step["status"] == "compensated"


def test_step2_completed(step_by_id):
    """Step 2 (create_backup) should complete then get compensated."""
    step = step_by_id["step_2"]
    assert step["status"] == "compensated"


def test_step3_fallback(step_by_id):
    """Step 3 (validate_data) fails but has fallback -> completed_with_fallback."""
    step = step_by_id["step_3"]
    assert step["status"] in ("completed_with_fallback", "completed"), (
        f"Step 3 should use fallback, got status: {step['status']}"
    )


def test_step4_completed(step_by_id):
    """Step 4 (transform_records) should complete then get compensated."""
    step = step_by_id["step_4"]
    assert step["status"] == "compensated"


def test_step5_completed(step_by_id):
    """Step 5 (update_table) should complete then get compensated."""
    step = step_by_id["step_5"]
    assert step["status"] == "compensated"


def test_step6_critical_failure(step_by_id):
    """Step 6 (sync_external) fails critically with no fallback -> failed."""
    step = step_by_id["step_6"]
    assert step["status"] == "failed"


def test_step7_skipped(step_by_id):
    """Step 7 should be skipped due to workflow abort."""
    step = step_by_id["step_7"]
    assert step["status"] == "skipped"


def test_step8_skipped(step_by_id):
    """Step 8 should be skipped due to workflow abort."""
    step = step_by_id["step_8"]
    assert step["status"] == "skipped"


def test_workflow_aborted(report):
    """Workflow should be aborted due to critical failure at step 6."""
    assert report["workflow_status"] == "aborted"


def test_compensations_executed(report):
    """Compensations should have been executed for steps 1,2,4,5 (compensatable completed steps)."""
    comp_step_ids = [c["step_id"] for c in report["compensations"]]
    assert len(comp_step_ids) == 4, f"Expected 4 compensations, got {len(comp_step_ids)}"
    assert set(comp_step_ids) == {"step_1", "step_2", "step_4", "step_5"}


def test_compensations_reverse_order(report):
    """Compensations must be in reverse order of completion."""
    comp_step_ids = [c["step_id"] for c in report["compensations"]]
    assert comp_step_ids == ["step_5", "step_4", "step_2", "step_1"], (
        f"Expected reverse order, got {comp_step_ids}"
    )


def test_summary_counts(report):
    """Summary counts must be accurate."""
    summary = report["summary"]
    # step_3 completed_with_fallback counts as completed
    # steps 1,2,4,5 compensated; step 6 failed; steps 7,8 skipped
    assert summary["failed_count"] == 1
    assert summary["compensated_count"] == 4
    assert summary["skipped_count"] == 2


# ── Enhanced checks (auto-generated) ────────────────────────────────────────

@pytest.mark.weight(1)
def test_no_placeholder_values(workspace):
    """Output files must not contain placeholder/TODO markers."""
    placeholders = ["PLACEHOLDER", "CHANGEME", "your_"]
    for f in workspace.iterdir():
        if f.is_file() and f.suffix in (".json", ".csv", ".txt", ".md", ".py", ".yaml", ".yml", ".html", ".xml"):
            content = f.read_text(errors="replace")
            for p in placeholders:
                assert p not in content, f"Placeholder '{p}' found in {f.name}"

@pytest.mark.weight(2)
def test_no_empty_critical_fields(workspace):
    """JSON output must not have empty-string or null values in top-level fields."""
    import json
    path = workspace / "workflow_steps.json"
    if not path.exists():
        pytest.skip("output file not found")
    data = json.loads(path.read_text())
    items = data if isinstance(data, list) else [data]
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        for k, v in item.items():
            assert v is not None, f"Item {i}: field '{k}' is null"
            if isinstance(v, str):
                assert v.strip() != "", f"Item {i}: field '{k}' is empty string"

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
    path = workspace / "workflow_steps.json"
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
    consistency = dominant / len(all_keys) if all_keys else 1
    assert consistency >= 0.7, f"Key naming inconsistent: {snake} snake, {camel} camel, {pascal} pascal out of {len(all_keys)} keys"

@pytest.mark.weight(1)
def test_no_duplicate_entries(workspace):
    """Output should not contain exact duplicate rows/objects."""
    import json
    path = workspace / "workflow_steps.json"
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
    bad_patterns = [".DS_Store", "Thumbs.db", ".log", ".bak", ".tmp"]
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
