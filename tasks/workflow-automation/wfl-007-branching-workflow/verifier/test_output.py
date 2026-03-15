"""Verifier for wfl-007: Branching Workflow with Decision Tree."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def processed(workspace):
    """Load the processed applications."""
    path = workspace / "processed_applications.json"
    assert path.exists(), "processed_applications.json not found"
    return json.loads(path.read_text())


@pytest.fixture
def app_by_id(processed):
    """Create a lookup dict by application ID."""
    return {a["id"]: a for a in processed}


def test_output_file_exists(workspace):
    """processed_applications.json must exist."""
    assert (workspace / "processed_applications.json").exists()


def test_all_applications_processed(processed):
    """All 8 applications must be in the output."""
    assert len(processed) == 8, f"Expected 8 applications, got {len(processed)}"


def test_all_have_required_fields(processed):
    """Each result must have all required fields."""
    required = {"id", "applicant", "status", "rate", "conditions", "rejection_reason", "path"}
    for app in processed:
        assert required.issubset(set(app.keys())), (
            f"App {app.get('id')} missing fields: {required - set(app.keys())}"
        )


def test_app001_approved_low_rate(app_by_id):
    """app_001: credit 780, ratio 30000/95000=0.316 <= 0.4 -> approved at 4.5%."""
    app = app_by_id["app_001"]
    assert app["status"] == "approved"
    assert app["rate"] == 4.5
    assert app["conditions"] == []
    assert app["rejection_reason"] is None


def test_app002_conditional_high_credit(app_by_id):
    """app_002: credit 720, ratio 35000/60000=0.583 > 0.4 -> conditional at 6.0%."""
    app = app_by_id["app_002"]
    assert app["status"] == "conditionally_approved"
    assert app["rate"] == 6.0
    assert "requires collateral" in app["conditions"]


def test_app003_conditional_manual(app_by_id):
    """app_003: credit 650, emp_years 4 >= 3 -> conditional at 7.5%."""
    app = app_by_id["app_003"]
    assert app["status"] == "conditionally_approved"
    assert app["rate"] == 7.5
    assert "requires co-signer" in app["conditions"]


def test_app004_rejected_credit(app_by_id):
    """app_004: credit 450 < 500 -> rejected (credit too low)."""
    app = app_by_id["app_004"]
    assert app["status"] == "rejected"
    assert app["rate"] is None
    assert "credit" in app["rejection_reason"].lower()


def test_app005_rejected_employment(app_by_id):
    """app_005: credit 580, emp_years 1 < 3 -> rejected (insufficient employment)."""
    app = app_by_id["app_005"]
    assert app["status"] == "rejected"
    assert "employment" in app["rejection_reason"].lower()


def test_app006_approved(app_by_id):
    """app_006: credit 810, ratio 50000/120000=0.417 > 0.4 -> conditional at 6.0%."""
    app = app_by_id["app_006"]
    assert app["status"] == "conditionally_approved"
    assert app["rate"] == 6.0


def test_app007_conditional_manual(app_by_id):
    """app_007: credit 690 (500-699), emp_years 6 >= 3 -> conditional at 7.5%."""
    app = app_by_id["app_007"]
    assert app["status"] == "conditionally_approved"
    assert app["rate"] == 7.5


def test_app008_conditional_high_credit(app_by_id):
    """app_008: credit 740, ratio 45000/55000=0.818 > 0.4 -> conditional at 6.0%."""
    app = app_by_id["app_008"]
    assert app["status"] == "conditionally_approved"
    assert app["rate"] == 6.0


def test_paths_start_with_initial_review(processed):
    """All paths must start with initial_review."""
    for app in processed:
        assert app["path"][0] == "initial_review", (
            f"App {app['id']} path doesn't start with initial_review: {app['path']}"
        )


def test_paths_have_minimum_length(processed):
    """All paths must have at least 2 steps."""
    for app in processed:
        assert len(app["path"]) >= 2, (
            f"App {app['id']} path too short: {app['path']}"
        )


def test_status_distribution(processed):
    """Should have 1 approved, 5 conditional, 2 rejected."""
    statuses = [a["status"] for a in processed]
    assert statuses.count("approved") == 1
    assert statuses.count("conditionally_approved") == 5
    assert statuses.count("rejected") == 2
