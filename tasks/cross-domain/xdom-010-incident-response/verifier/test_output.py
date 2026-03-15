"""Verifier for xdom-010: Incident Response Workflow."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def timeline(workspace):
    path = workspace / "timeline.json"
    assert path.exists(), "timeline.json not found"
    with open(path) as f:
        return json.load(f)


@pytest.fixture
def root_cause(workspace):
    path = workspace / "root_cause.md"
    assert path.exists(), "root_cause.md not found"
    return path.read_text()


@pytest.fixture
def remediation(workspace):
    path = workspace / "remediation_plan.json"
    assert path.exists(), "remediation_plan.json not found"
    with open(path) as f:
        return json.load(f)


@pytest.fixture
def communication(workspace):
    path = workspace / "communication_draft.md"
    assert path.exists(), "communication_draft.md not found"
    return path.read_text()


def test_timeline_exists(workspace):
    """timeline.json must exist."""
    assert (workspace / "timeline.json").exists()


def test_root_cause_exists(workspace):
    """root_cause.md must exist."""
    assert (workspace / "root_cause.md").exists()


def test_remediation_exists(workspace):
    """remediation_plan.json must exist."""
    assert (workspace / "remediation_plan.json").exists()


def test_communication_exists(workspace):
    """communication_draft.md must exist."""
    assert (workspace / "communication_draft.md").exists()


def test_timeline_has_events(timeline):
    """Timeline must have events."""
    events = timeline.get("events", [])
    assert len(events) >= 8, f"Expected at least 8 timeline events, got {len(events)}"


def test_timeline_events_have_fields(timeline):
    """Each event must have timestamp, source, and description."""
    for i, event in enumerate(timeline.get("events", [])):
        assert "timestamp" in event, f"Event {i} missing timestamp"
        assert "description" in event, f"Event {i} missing description"


def test_timeline_covers_config_change(timeline):
    """Timeline must include the config change event."""
    descriptions = " ".join(e.get("description", "").lower() for e in timeline.get("events", []))
    assert "config" in descriptions or "rate limit" in descriptions, \
        "Timeline should reference the configuration change"


def test_timeline_covers_resolution(timeline):
    """Timeline must include resolution events."""
    descriptions = " ".join(e.get("description", "").lower() for e in timeline.get("events", []))
    assert "rollback" in descriptions or "restored" in descriptions or "resume" in descriptions, \
        "Timeline should cover incident resolution"


def test_root_cause_identifies_config(root_cause):
    """Root cause must identify the config change as the cause."""
    lower = root_cause.lower()
    assert "config" in lower or "rate limit" in lower, \
        "Root cause should mention configuration/rate limit change"


def test_root_cause_has_contributing_factors(root_cause):
    """Root cause must list contributing factors."""
    lower = root_cause.lower()
    assert "factor" in lower or "contribut" in lower or "cause" in lower, \
        "Root cause should discuss contributing factors"


def test_root_cause_has_evidence(root_cause):
    """Root cause should reference evidence from the data."""
    lower = root_cause.lower()
    has_evidence = "evidence" in lower or "log" in lower or "alert" in lower or "timestamp" in lower
    assert has_evidence, "Root cause should reference evidence"


def test_remediation_has_three_categories(remediation):
    """Remediation must have immediate, short-term, and long-term actions."""
    assert "immediate_actions" in remediation, "Missing immediate_actions"
    assert "short_term_fixes" in remediation, "Missing short_term_fixes"
    assert "long_term_improvements" in remediation, "Missing long_term_improvements"


def test_remediation_actions_have_fields(remediation):
    """Each remediation action must have description, owner, priority, and deadline."""
    required = {"description", "owner", "priority"}
    for category in ["immediate_actions", "short_term_fixes", "long_term_improvements"]:
        for i, action in enumerate(remediation.get(category, [])):
            missing = required - set(action.keys())
            assert not missing, f"{category}[{i}] missing: {missing}"


def test_remediation_has_minimum_actions(remediation):
    """Each category must have at least one action."""
    assert len(remediation.get("immediate_actions", [])) >= 1
    assert len(remediation.get("short_term_fixes", [])) >= 1
    assert len(remediation.get("long_term_improvements", [])) >= 1


def test_communication_has_summary(communication):
    """Communication must have an incident summary."""
    lower = communication.lower()
    assert "summary" in lower or "overview" in lower


def test_communication_has_impact(communication):
    """Communication must describe the impact."""
    lower = communication.lower()
    assert "impact" in lower


def test_communication_has_status(communication):
    """Communication must include current status."""
    lower = communication.lower()
    assert "status" in lower or "resolved" in lower or "restored" in lower


def test_communication_has_contact(communication):
    """Communication must include a contact person."""
    lower = communication.lower()
    assert "contact" in lower or "@" in communication
