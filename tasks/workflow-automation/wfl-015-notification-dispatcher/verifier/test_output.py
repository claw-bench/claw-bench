"""Verifier for wfl-015: Notification Dispatcher."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return request.config.getoption("--workspace")


@pytest.fixture
def dispatch_log(workspace):
    path = Path(workspace) / "dispatch_log.jsonl"
    assert path.exists(), "dispatch_log.jsonl not found in workspace"
    entries = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries


@pytest.fixture
def dispatch_map(dispatch_log):
    return {e["event_id"]: e for e in dispatch_log}


def test_output_file_exists(workspace):
    assert (Path(workspace) / "dispatch_log.jsonl").exists()


def test_correct_event_count(dispatch_log):
    assert len(dispatch_log) == 15, f"Expected 15 entries, got {len(dispatch_log)}"


def test_entry_structure(dispatch_log):
    for entry in dispatch_log:
        assert "event_id" in entry
        assert "matched_rules" in entry
        assert "channels" in entry
        assert isinstance(entry["matched_rules"], list)
        assert isinstance(entry["channels"], list)


def test_channels_sorted(dispatch_log):
    for entry in dispatch_log:
        assert entry["channels"] == sorted(entry["channels"]), \
            f"Channels not sorted for {entry['event_id']}"


def test_channels_deduplicated(dispatch_log):
    for entry in dispatch_log:
        assert len(entry["channels"]) == len(set(entry["channels"])), \
            f"Duplicate channels for {entry['event_id']}"


def test_critical_incident_e3(dispatch_map):
    """E3: critical incident from pagerduty - matches critical-all-channels."""
    e = dispatch_map["E3"]
    assert "critical-all-channels" in e["matched_rules"]
    for ch in ["email", "pagerduty", "slack", "sms"]:
        assert ch in e["channels"]


def test_high_alert_e2(dispatch_map):
    """E2: high alert from monitoring - matches high-severity-alerts and monitoring-medium-plus."""
    e = dispatch_map["E2"]
    assert "high-severity-alerts" in e["matched_rules"]
    assert "monitoring-medium-plus" in e["matched_rules"]
    assert "slack" in e["channels"]
    assert "pagerduty" in e["channels"]


def test_deployment_e1(dispatch_map):
    """E1: deployment low from ci-server - matches deployment-notifications only."""
    e = dispatch_map["E1"]
    assert "deployment-notifications" in e["matched_rules"]
    assert "slack" in e["channels"]
    assert "email" in e["channels"]


def test_maintenance_no_match(dispatch_map):
    """E9: maintenance low from scheduler - matches no rules."""
    e = dispatch_map["E9"]
    assert len(e["matched_rules"]) == 0
    assert len(e["channels"]) == 0


def test_maintenance_e14_no_match(dispatch_map):
    """E14: maintenance low from scheduler - matches no rules."""
    e = dispatch_map["E14"]
    assert len(e["matched_rules"]) == 0
    assert len(e["channels"]) == 0


def test_security_event_e13(dispatch_map):
    """E13: high alert from security - matches high-severity-alerts and security-events."""
    e = dispatch_map["E13"]
    assert "high-severity-alerts" in e["matched_rules"]
    assert "security-events" in e["matched_rules"]
    assert "pagerduty" in e["channels"]


def test_critical_monitoring_e7(dispatch_map):
    """E7: critical alert from monitoring - matches critical-all-channels and monitoring-medium-plus."""
    e = dispatch_map["E7"]
    assert "critical-all-channels" in e["matched_rules"]
    assert "monitoring-medium-plus" in e["matched_rules"]
    assert "sms" in e["channels"]


def test_security_incident_e15(dispatch_map):
    """E15: high incident from security - matches high-severity-alerts and security-events."""
    e = dispatch_map["E15"]
    assert "high-severity-alerts" in e["matched_rules"]
    assert "security-events" in e["matched_rules"]
