"""Verifier for xdom-017: Build Business Travel Itinerary."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def itinerary(workspace):
    """Read and return the itinerary.json contents."""
    path = workspace / "itinerary.json"
    assert path.exists(), "itinerary.json not found in workspace"
    return json.loads(path.read_text())


def test_itinerary_exists(workspace):
    """itinerary.json must exist in the workspace."""
    assert (workspace / "itinerary.json").exists()


def test_total_days(itinerary):
    """Total days should be 3."""
    assert itinerary["total_days"] == 3


def test_total_meetings(itinerary):
    """Total meetings should be 3."""
    assert itinerary["total_meetings"] == 3


def test_days_count(itinerary):
    """Should have 3 day entries."""
    assert len(itinerary["days"]) == 3


def test_day1_date(itinerary):
    """Day 1 should be 2026-03-25."""
    assert itinerary["days"][0]["date"] == "2026-03-25"


def test_day2_date(itinerary):
    """Day 2 should be 2026-03-26."""
    assert itinerary["days"][1]["date"] == "2026-03-26"


def test_day3_date(itinerary):
    """Day 3 should be 2026-03-27."""
    assert itinerary["days"][2]["date"] == "2026-03-27"


def test_day1_has_outbound_flight(itinerary):
    """Day 1 should have a flight event mentioning UA-1234."""
    day1 = itinerary["days"][0]
    flight_events = [e for e in day1["events"] if e["type"] == "flight"]
    assert len(flight_events) >= 1, "Day 1 should have at least one flight event"
    flight_text = " ".join(e["description"] for e in flight_events)
    assert "UA-1234" in flight_text, "Day 1 flight should mention UA-1234"


def test_day1_has_hotel_checkin(itinerary):
    """Day 1 should have a hotel check-in event."""
    day1 = itinerary["days"][0]
    hotel_events = [e for e in day1["events"] if e["type"] == "hotel"]
    assert len(hotel_events) >= 1, "Day 1 should have a hotel event"


def test_day2_has_three_meetings(itinerary):
    """Day 2 should have 3 meeting events."""
    day2 = itinerary["days"][1]
    meeting_events = [e for e in day2["events"] if e["type"] == "meeting"]
    assert len(meeting_events) == 3, f"Day 2 should have 3 meetings, got {len(meeting_events)}"


def test_day2_meeting_times(itinerary):
    """Day 2 meetings should be at 09:00, 14:00, and 19:00."""
    day2 = itinerary["days"][1]
    meeting_events = [e for e in day2["events"] if e["type"] == "meeting"]
    times = sorted(e["time"] for e in meeting_events)
    assert times == ["09:00", "14:00", "19:00"]


def test_day3_has_return_flight(itinerary):
    """Day 3 should have a flight event mentioning UA-5678."""
    day3 = itinerary["days"][2]
    flight_events = [e for e in day3["events"] if e["type"] == "flight"]
    assert len(flight_events) >= 1, "Day 3 should have at least one flight event"
    flight_text = " ".join(e["description"] for e in flight_events)
    assert "UA-5678" in flight_text, "Day 3 flight should mention UA-5678"


def test_day3_has_hotel_checkout(itinerary):
    """Day 3 should have a hotel check-out event."""
    day3 = itinerary["days"][2]
    hotel_events = [e for e in day3["events"] if e["type"] == "hotel"]
    assert len(hotel_events) >= 1, "Day 3 should have a hotel event"


def test_hotel_confirmation_appears(itinerary):
    """Hotel confirmation number HLT-98765 should appear somewhere in the itinerary."""
    full_text = json.dumps(itinerary)
    assert "HLT-98765" in full_text, "Hotel confirmation HLT-98765 should appear in itinerary"


def test_dates_range(itinerary):
    """Dates field should span from 2026-03-25 to 2026-03-27."""
    dates = itinerary["dates"]
    assert "2026-03-25" in dates
    assert "2026-03-27" in dates


def test_new_york_in_traveler(itinerary):
    """Traveler field should mention New York."""
    assert "New York" in itinerary["traveler"] or "JFK" in itinerary["traveler"]


# ── Enhanced checks (auto-generated) ────────────────────────────────────────

@pytest.mark.weight(1)
def test_no_placeholder_values(workspace):
    """Output files must not contain placeholder/TODO markers."""
    placeholders = ["PLACEHOLDER", "CHANGEME"]
    for f in workspace.iterdir():
        if f.is_file() and f.suffix in (".json", ".csv", ".txt", ".md", ".py", ".yaml", ".yml", ".html", ".xml"):
            content = f.read_text(errors="replace")
            for p in placeholders:
                assert p not in content, f"Placeholder '{p}' found in {f.name}"

@pytest.mark.weight(2)
def test_no_empty_critical_fields(workspace):
    """JSON output must not have empty-string or null values in top-level fields."""
    import json
    path = workspace / "flight_booking.json"
    if not path.exists():
        pytest.skip("output file not found")
    data = json.loads(path.read_text())
    items = data if isinstance(data, list) else [data]
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        non_empty = [
            v for v in item.values()
            if v is not None and (not isinstance(v, str) or v.strip() != "")
        ]
        assert non_empty, f"Item {i}: all fields are empty or null"

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
    path = workspace / "flight_booking.json"
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
    classified = snake + camel + pascal
    if classified == 0:
        return
    consistency = dominant / classified
    assert consistency >= 0.7, f"Key naming inconsistent: {snake} snake, {camel} camel, {pascal} pascal out of {len(all_keys)} keys"

@pytest.mark.weight(1)
def test_no_duplicate_entries(workspace):
    """Output should not contain exact duplicate rows/objects."""
    import json
    path = workspace / "flight_booking.json"
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
    bad_patterns = [".DS_Store", "Thumbs.db", ".bak", ".tmp"]
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
