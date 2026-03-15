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
