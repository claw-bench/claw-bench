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
