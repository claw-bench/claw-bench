"""Verifier for xdom-004: Log to Alert."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def alerts(workspace):
    path = workspace / "alerts.json"
    assert path.exists(), "alerts.json not found"
    with open(path) as f:
        data = json.load(f)
    assert isinstance(data, list)
    return data


@pytest.fixture
def incident_report(workspace):
    path = workspace / "incident_report.md"
    assert path.exists(), "incident_report.md not found"
    return path.read_text()


def test_alerts_file_exists(workspace):
    """alerts.json must exist."""
    assert (workspace / "alerts.json").exists()


def test_incident_report_exists(workspace):
    """incident_report.md must exist."""
    assert (workspace / "incident_report.md").exists()


def test_three_alerts_triggered(alerts):
    """All 3 alert rules should be triggered."""
    assert len(alerts) == 3, f"Expected 3 alerts, got {len(alerts)}"


def test_alert_required_fields(alerts):
    """Each alert must have required fields."""
    required = {"rule_id", "rule_name", "severity", "message"}
    for i, alert in enumerate(alerts):
        missing = required - set(alert.keys())
        assert not missing, f"Alert {i} missing fields: {missing}"


def test_high_error_rate_alert(alerts):
    """High Error Rate alert (rule-001) must be present."""
    matches = [a for a in alerts if a.get("rule_id") == "rule-001" or "error rate" in a.get("rule_name", "").lower()]
    assert len(matches) >= 1, "High Error Rate alert not found"
    alert = matches[0]
    assert alert["severity"] in ("critical", "high")


def test_database_failure_alert(alerts):
    """Database Connection Failure alert (rule-002) must be present."""
    matches = [a for a in alerts if a.get("rule_id") == "rule-002" or "database" in a.get("rule_name", "").lower()]
    assert len(matches) >= 1, "Database Connection Failure alert not found"
    alert = matches[0]
    assert alert["severity"] == "critical"


def test_memory_threshold_alert(alerts):
    """Memory Threshold alert (rule-003) must be present."""
    matches = [a for a in alerts if a.get("rule_id") == "rule-003" or "memory" in a.get("rule_name", "").lower()]
    assert len(matches) >= 1, "Memory Threshold Exceeded alert not found"
    alert = matches[0]
    assert alert["severity"] in ("critical", "high")


def test_report_has_timeline(incident_report):
    """Incident report must have a timeline section."""
    lower = incident_report.lower()
    assert "timeline" in lower, "No timeline section in incident report"


def test_report_timeline_has_key_events(incident_report):
    """Timeline must mention key events."""
    lower = incident_report.lower()
    assert "database" in lower, "Timeline should mention database events"
    assert "memory" in lower or "gc" in lower, "Timeline should mention memory/GC events"


def test_report_has_alerts_section(incident_report):
    """Incident report must summarize the alerts."""
    lower = incident_report.lower()
    assert "alert" in lower, "No alerts section in incident report"


def test_report_has_impact_or_recommendations(incident_report):
    """Report must have impact assessment or recommended actions."""
    lower = incident_report.lower()
    has_impact = "impact" in lower
    has_recommend = "recommend" in lower or "action" in lower or "remediat" in lower
    assert has_impact or has_recommend, "Report missing impact assessment or recommendations"


def test_alert_severities_valid(alerts):
    """All alert severities must be valid values."""
    valid = {"low", "medium", "high", "critical"}
    for alert in alerts:
        assert alert["severity"] in valid, f"Invalid severity: {alert['severity']}"
