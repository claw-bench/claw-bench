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
    path = workspace / "emails.json"
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
    path = workspace / "emails.json"
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
    path = workspace / "emails.json"
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
