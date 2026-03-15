"""Verifier for sec-011: Incident Response Plan."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def response_plan(workspace):
    """Load and return the response plan markdown."""
    path = workspace / "response_plan.md"
    assert path.exists(), "response_plan.md not found in workspace"
    return path.read_text()


@pytest.fixture
def timeline(workspace):
    """Load and return the timeline JSON."""
    path = workspace / "timeline.json"
    assert path.exists(), "timeline.json not found in workspace"
    data = json.loads(path.read_text())
    assert isinstance(data, list), "timeline.json must contain a JSON array"
    return data


def test_response_plan_exists(workspace):
    """response_plan.md must exist."""
    assert (workspace / "response_plan.md").exists()


def test_timeline_exists(workspace):
    """timeline.json must exist."""
    assert (workspace / "timeline.json").exists()


def test_plan_has_incident_summary(response_plan):
    """Response plan must include an incident summary section."""
    lower = response_plan.lower()
    assert "summary" in lower or "incident" in lower


def test_plan_references_affected_systems(response_plan):
    """Response plan must reference the affected systems."""
    assert "app-srv-03" in response_plan or "app_srv_03" in response_plan
    assert "db-primary" in response_plan or "db_primary" in response_plan or "database" in response_plan.lower()


def test_plan_references_correct_playbook(response_plan):
    """Response plan must reference the data breach playbook (PB-002)."""
    lower = response_plan.lower()
    assert "pb-002" in lower or "data breach" in lower or "breach response" in lower


def test_plan_has_containment_steps(response_plan):
    """Response plan must include containment/immediate actions."""
    lower = response_plan.lower()
    assert "contain" in lower or "immediate" in lower or "isolat" in lower


def test_plan_has_communication_section(response_plan):
    """Response plan must include a communication plan."""
    lower = response_plan.lower()
    assert "communicat" in lower or "notif" in lower or "legal" in lower


def test_plan_mentions_credential_revocation(response_plan):
    """Response plan must mention revoking compromised credentials."""
    lower = response_plan.lower()
    assert "revok" in lower or "disable" in lower or "reset" in lower or "credential" in lower


def test_timeline_has_minimum_events(timeline):
    """Timeline must include at least the 5 known events plus response milestones."""
    assert len(timeline) >= 7, f"Expected at least 7 timeline events, got {len(timeline)}"


def test_timeline_events_have_required_fields(timeline):
    """Each timeline event must have timestamp, event, source."""
    for entry in timeline:
        assert "timestamp" in entry, "Missing 'timestamp' field"
        assert "event" in entry, "Missing 'event' field"
        assert "source" in entry, "Missing 'source' field"


def test_timeline_includes_initial_compromise(timeline):
    """Timeline must include the initial authentication event at 08:15."""
    events_text = " ".join(e["event"] for e in timeline).lower()
    assert "08:15" in " ".join(e["timestamp"] for e in timeline) or "authenticat" in events_text


def test_timeline_includes_data_exfiltration(timeline):
    """Timeline must include the data transfer spike."""
    events_text = " ".join(e["event"] for e in timeline).lower()
    assert "transfer" in events_text or "exfiltrat" in events_text or "2.3" in events_text or "outbound" in events_text
