"""Verifier for mem-015: Timeline Reconstructor."""

import json
import pytest
from pathlib import Path


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


def _load(workspace):
    return json.loads((workspace / "timeline.json").read_text())


def test_file_exists(workspace):
    assert (workspace / "timeline.json").exists(), "timeline.json not found"


def test_valid_json(workspace):
    try:
        _load(workspace)
    except json.JSONDecodeError as e:
        pytest.fail(f"timeline.json is not valid JSON: {e}")


def test_has_required_keys(workspace):
    data = _load(workspace)
    for key in ["events", "total_events", "earliest_date", "latest_date"]:
        assert key in data, f"Missing key: {key}"


def test_total_events(workspace):
    data = _load(workspace)
    assert data["total_events"] == 10, f"Expected 10 events, got {data['total_events']}"


def test_event_count(workspace):
    data = _load(workspace)
    assert len(data["events"]) == 10, f"Expected 10 events in list, got {len(data['events'])}"


def test_e1_date(workspace):
    """E1: anchor 2025-03-03."""
    data = _load(workspace)
    e1 = [e for e in data["events"] if e["id"] == "E1"][0]
    assert e1["date"] == "2025-03-03"


def test_e2_date(workspace):
    """E2: 5 days after E1 = 2025-03-08."""
    data = _load(workspace)
    e2 = [e for e in data["events"] if e["id"] == "E2"][0]
    assert e2["date"] == "2025-03-08", f"Expected 2025-03-08, got {e2['date']}"


def test_e3_date(workspace):
    """E3: 2 days after E2 = 2025-03-10."""
    data = _load(workspace)
    e3 = [e for e in data["events"] if e["id"] == "E3"][0]
    assert e3["date"] == "2025-03-10", f"Expected 2025-03-10, got {e3['date']}"


def test_e4_date(workspace):
    """E4: 1 week after E3 = 2025-03-17."""
    data = _load(workspace)
    e4 = [e for e in data["events"] if e["id"] == "E4"][0]
    assert e4["date"] == "2025-03-17", f"Expected 2025-03-17, got {e4['date']}"


def test_e5_date(workspace):
    """E5: 3 days after E4 = 2025-03-20."""
    data = _load(workspace)
    e5 = [e for e in data["events"] if e["id"] == "E5"][0]
    assert e5["date"] == "2025-03-20", f"Expected 2025-03-20, got {e5['date']}"


def test_e6_date(workspace):
    """E6: anchor 2025-03-24."""
    data = _load(workspace)
    e6 = [e for e in data["events"] if e["id"] == "E6"][0]
    assert e6["date"] == "2025-03-24"


def test_e7_date(workspace):
    """E7: 4 days after E6 = 2025-03-28."""
    data = _load(workspace)
    e7 = [e for e in data["events"] if e["id"] == "E7"][0]
    assert e7["date"] == "2025-03-28", f"Expected 2025-03-28, got {e7['date']}"


def test_e8_date(workspace):
    """E8: 1 week after E7 = 2025-04-04."""
    data = _load(workspace)
    e8 = [e for e in data["events"] if e["id"] == "E8"][0]
    assert e8["date"] == "2025-04-04", f"Expected 2025-04-04, got {e8['date']}"


def test_e9_date(workspace):
    """E9: anchor 2025-04-08."""
    data = _load(workspace)
    e9 = [e for e in data["events"] if e["id"] == "E9"][0]
    assert e9["date"] == "2025-04-08"


def test_e10_date(workspace):
    """E10: 5 days after E9 = 2025-04-13."""
    data = _load(workspace)
    e10 = [e for e in data["events"] if e["id"] == "E10"][0]
    assert e10["date"] == "2025-04-13", f"Expected 2025-04-13, got {e10['date']}"


def test_chronological_order(workspace):
    """Events must be sorted chronologically."""
    data = _load(workspace)
    dates = [e["date"] for e in data["events"]]
    assert dates == sorted(dates), f"Events not in chronological order: {dates}"


def test_earliest_date(workspace):
    data = _load(workspace)
    assert data["earliest_date"] == "2025-03-03"


def test_latest_date(workspace):
    data = _load(workspace)
    assert data["latest_date"] == "2025-04-13"


def test_event_structure(workspace):
    """Each event must have id, event, date."""
    data = _load(workspace)
    for event in data["events"]:
        assert "id" in event, "Event missing 'id'"
        assert "event" in event, "Event missing 'event'"
        assert "date" in event, "Event missing 'date'"
