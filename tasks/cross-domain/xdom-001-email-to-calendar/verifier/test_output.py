"""Verifier for xdom-001: Email to Calendar."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def calendar_entries(workspace):
    path = workspace / "calendar_entries.json"
    assert path.exists(), "calendar_entries.json not found in workspace"
    with open(path) as f:
        data = json.load(f)
    assert isinstance(data, list), "calendar_entries.json must be a JSON array"
    return data


def test_calendar_file_exists(workspace):
    """calendar_entries.json must exist."""
    assert (workspace / "calendar_entries.json").exists()


def test_exactly_four_meetings(calendar_entries):
    """There should be exactly 4 meeting invitations extracted."""
    assert len(calendar_entries) == 4, f"Expected 4 meetings, got {len(calendar_entries)}"


def test_each_entry_has_required_fields(calendar_entries):
    """Each calendar entry must have all required fields."""
    required = {"subject", "date", "start_time", "duration_minutes", "participants", "organizer"}
    for i, entry in enumerate(calendar_entries):
        missing = required - set(entry.keys())
        assert not missing, f"Entry {i} missing fields: {missing}"


def test_dates_are_valid_iso(calendar_entries):
    """All dates must be in YYYY-MM-DD format."""
    import re
    pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    for entry in calendar_entries:
        assert pattern.match(entry["date"]), f"Invalid date format: {entry['date']}"


def test_times_are_24h_format(calendar_entries):
    """All start times must be in HH:MM 24-hour format."""
    import re
    pattern = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d$")
    for entry in calendar_entries:
        assert pattern.match(entry["start_time"]), f"Invalid time format: {entry['start_time']}"


def test_q1_planning_meeting(calendar_entries):
    """Q1 Planning Meeting must be correctly extracted."""
    matches = [e for e in calendar_entries if "Q1" in e.get("subject", "") or "Planning" in e.get("subject", "")]
    assert len(matches) >= 1, "Q1 Planning Meeting not found"
    m = matches[0]
    assert m["date"] == "2026-04-01"
    assert m["start_time"] == "10:00"
    assert m["duration_minutes"] == 90
    assert "bob@techcorp.com" in m["participants"]
    assert "carol@techcorp.com" in m["participants"]
    assert m["organizer"] == "alice@techcorp.com"


def test_sprint_retrospective(calendar_entries):
    """Sprint Retrospective must be correctly extracted."""
    matches = [e for e in calendar_entries if "Sprint" in e.get("subject", "") or "Retrospective" in e.get("subject", "")]
    assert len(matches) >= 1, "Sprint Retrospective not found"
    m = matches[0]
    assert m["date"] == "2026-04-03"
    assert m["start_time"] == "14:00"
    assert m["duration_minutes"] == 60
    assert m["organizer"] == "bob@techcorp.com"
    assert len(m["participants"]) == 3


def test_design_review(calendar_entries):
    """Design Review Session must be correctly extracted."""
    matches = [e for e in calendar_entries if "Design" in e.get("subject", "") or "Review" in e.get("subject", "")]
    assert len(matches) >= 1, "Design Review Session not found"
    m = matches[0]
    assert m["date"] == "2026-04-07"
    assert m["start_time"] == "11:30"
    assert m["duration_minutes"] == 45
    assert m["organizer"] == "dave@techcorp.com"


def test_client_demo(calendar_entries):
    """Client Demo Preparation must be correctly extracted."""
    matches = [e for e in calendar_entries if "Client" in e.get("subject", "") or "Demo" in e.get("subject", "")]
    assert len(matches) >= 1, "Client Demo Preparation not found"
    m = matches[0]
    assert m["date"] == "2026-04-10"
    assert m["start_time"] == "15:00"
    assert m["duration_minutes"] == 120
    assert len(m["participants"]) == 4
    assert m["organizer"] == "carol@techcorp.com"


def test_no_non_meeting_emails_included(calendar_entries):
    """Regular emails must not be included as meetings."""
    subjects = [e.get("subject", "").lower() for e in calendar_entries]
    for bad in ["lunch", "budget", "conference", "vacation", "office closure", "project update"]:
        assert not any(bad in s for s in subjects), f"Non-meeting email '{bad}' should not be in calendar entries"
