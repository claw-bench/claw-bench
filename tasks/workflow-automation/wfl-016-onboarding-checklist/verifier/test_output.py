"""Verifier for wfl-016: Process Employee Onboarding Checklist."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def account_setup(workspace):
    """Read and return the account_setup.json contents."""
    path = workspace / "account_setup.json"
    assert path.exists(), "account_setup.json not found in workspace"
    return json.loads(path.read_text())


@pytest.fixture
def welcome_email(workspace):
    """Read and return the welcome_email.json contents."""
    path = workspace / "welcome_email.json"
    assert path.exists(), "welcome_email.json not found in workspace"
    return json.loads(path.read_text())


@pytest.fixture
def equipment_request(workspace):
    """Read and return the equipment_request.json contents."""
    path = workspace / "equipment_request.json"
    assert path.exists(), "equipment_request.json not found in workspace"
    return json.loads(path.read_text())


# --- account_setup.json tests ---


def test_account_setup_exists(workspace):
    """account_setup.json must exist in the workspace."""
    assert (workspace / "account_setup.json").exists()


def test_account_setup_username(account_setup):
    """Username should be derived from email prefix."""
    assert account_setup["username"] == "emily.zhang"


def test_account_setup_email(account_setup):
    """Email should match the new hire email."""
    assert account_setup["email"] == "emily.zhang@company.com"


def test_account_setup_groups_contains_engineering(account_setup):
    """Groups should contain 'engineering' (lowercase department)."""
    groups = [g.lower() for g in account_setup["groups"]]
    assert "engineering" in groups


def test_account_setup_groups_contains_all_staff(account_setup):
    """Groups should contain 'all-staff'."""
    groups = [g.lower() for g in account_setup["groups"]]
    assert "all-staff" in groups


def test_account_setup_access_level(account_setup):
    """Access level should be 'developer' for Engineering department."""
    assert account_setup["access_level"] == "developer"


# --- welcome_email.json tests ---


def test_welcome_email_exists(workspace):
    """welcome_email.json must exist in the workspace."""
    assert (workspace / "welcome_email.json").exists()


def test_welcome_email_to(welcome_email):
    """To field should be the employee's email."""
    assert welcome_email["to"] == "emily.zhang@company.com"


def test_welcome_email_cc(welcome_email):
    """CC field should contain the manager's email."""
    assert welcome_email["cc"] == "david.park@company.com"


def test_welcome_email_subject_contains_name(welcome_email):
    """Subject should contain the employee's first name."""
    assert "Emily" in welcome_email["subject"]


def test_welcome_email_body_mentions_department(welcome_email):
    """Body should mention the department."""
    assert "Engineering" in welcome_email["body"]


def test_welcome_email_body_mentions_manager(welcome_email):
    """Body should mention the manager's name."""
    assert "David Park" in welcome_email["body"]


def test_welcome_email_body_mentions_start_date(welcome_email):
    """Body should mention the start date."""
    body = welcome_email["body"]
    assert "March 23" in body or "2026-03-23" in body


# --- equipment_request.json tests ---


def test_equipment_request_exists(workspace):
    """equipment_request.json must exist in the workspace."""
    assert (workspace / "equipment_request.json").exists()


def test_equipment_request_employee(equipment_request):
    """Employee name should match."""
    assert equipment_request["employee"] == "Emily Zhang"


def test_equipment_request_department(equipment_request):
    """Department should match."""
    assert equipment_request["department"] == "Engineering"


def test_equipment_request_items_count(equipment_request):
    """Engineering department should have 4 equipment items."""
    assert len(equipment_request["items"]) == 4


def test_equipment_request_items_content(equipment_request):
    """Items should match the Engineering department equipment list."""
    expected = ["MacBook Pro 16\"", "External Monitor 27\"", "Mechanical Keyboard", "Standing Desk"]
    assert sorted(equipment_request["items"]) == sorted(expected)


def test_equipment_request_delivery_date(equipment_request):
    """Delivery date should be 3 days before start date (2026-03-20)."""
    assert equipment_request["delivery_date"] == "2026-03-20"
