"""Verifier for mem-003: Context Carry-Over."""

import pytest
from pathlib import Path


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


def test_db_connection_exists(workspace):
    """db_connection.txt must exist."""
    assert (workspace / "db_connection.txt").exists(), "db_connection.txt not found"


def test_db_connection_string(workspace):
    """db_connection.txt must contain the correct PostgreSQL connection string."""
    content = (workspace / "db_connection.txt").read_text().strip()
    assert content == "postgresql://app_service:xK9#mP2$vL5n@db.internal.example.com:5432/inventory_prod", (
        f"Incorrect connection string: {content}"
    )


def test_feature_report_exists(workspace):
    """feature_report.txt must exist."""
    assert (workspace / "feature_report.txt").exists(), "feature_report.txt not found"


def test_feature_report_content(workspace):
    """feature_report.txt must list all features with correct ENABLED/DISABLED status."""
    content = (workspace / "feature_report.txt").read_text().strip()
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    assert len(lines) == 5, f"Expected 5 feature lines, got {len(lines)}"

    expected = {
        "dark_mode": "ENABLED",
        "beta_dashboard": "DISABLED",
        "export_csv": "ENABLED",
        "multi_language": "DISABLED",
        "audit_logging": "ENABLED",
    }

    for line in lines:
        parts = line.split(":")
        name = parts[0].strip()
        status = parts[1].strip()
        assert name in expected, f"Unexpected feature: {name}"
        assert status == expected[name], (
            f"Feature '{name}' should be {expected[name]}, got {status}"
        )


def test_feature_report_order(workspace):
    """Features must appear in the same order as in config.json."""
    content = (workspace / "feature_report.txt").read_text().strip()
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    names = [line.split(":")[0].strip() for line in lines]
    expected_order = ["dark_mode", "beta_dashboard", "export_csv", "multi_language", "audit_logging"]
    assert names == expected_order, f"Features not in expected order: {names}"


def test_notification_summary_exists(workspace):
    """notification_summary.txt must exist."""
    assert (workspace / "notification_summary.txt").exists(), (
        "notification_summary.txt not found"
    )


def test_notification_email(workspace):
    """Notification summary must show email as on with correct recipient."""
    content = (workspace / "notification_summary.txt").read_text()
    assert "Email notifications: on" in content, "Email should be on"
    assert "ops-team@example.com" in content, "Email recipient missing"


def test_notification_sms(workspace):
    """Notification summary must show SMS as off with correct phone."""
    content = (workspace / "notification_summary.txt").read_text()
    assert "SMS notifications: off" in content, "SMS should be off"
    assert "+1-555-0142" in content, "SMS phone missing"


def test_notification_slack(workspace):
    """Slack webhook should be 'not configured' since no URL is provided."""
    content = (workspace / "notification_summary.txt").read_text()
    assert "not configured" in content.lower(), (
        "Slack webhook should show 'not configured'"
    )
