"""Verifier for data-014: Time Series Aggregation."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def report(workspace):
    """Read and parse aggregated.json."""
    path = workspace / "aggregated.json"
    assert path.exists(), "aggregated.json not found in workspace"
    return json.loads(path.read_text())


def test_output_file_exists(workspace):
    """aggregated.json must exist in the workspace."""
    assert (workspace / "aggregated.json").exists()


def test_top_level_keys(report):
    """Report must contain daily and trend keys."""
    assert "daily" in report, "Missing 'daily' key"
    assert "trend" in report, "Missing 'trend' key"


def test_daily_count(report):
    """There should be exactly 3 daily entries (Mar 1, 2, 3)."""
    assert len(report["daily"]) == 3, f"Expected 3 daily entries, got {len(report['daily'])}"


def test_daily_structure(report):
    """Each daily entry must have required fields."""
    required = {"date", "avg_cpu", "max_cpu", "avg_memory", "total_requests"}
    for entry in report["daily"]:
        assert required.issubset(entry.keys()), f"Missing keys: {required - entry.keys()}"


def test_daily_sorted_by_date(report):
    """Daily entries must be sorted by date ascending."""
    dates = [d["date"] for d in report["daily"]]
    assert dates == sorted(dates), "Daily entries not sorted by date"


def test_daily_dates(report):
    """Dates should be 2025-03-01, 2025-03-02, 2025-03-03."""
    dates = [d["date"] for d in report["daily"]]
    assert dates == ["2025-03-01", "2025-03-02", "2025-03-03"]


def test_day1_avg_cpu(report):
    """Day 1 avg CPU should be approximately 40.38 (within tolerance)."""
    day1 = report["daily"][0]
    assert abs(day1["avg_cpu"] - 40.38) < 1.0, f"Day 1 avg_cpu expected ~40.38, got {day1['avg_cpu']}"


def test_day1_max_cpu(report):
    """Day 1 max CPU should be 70.2."""
    day1 = report["daily"][0]
    assert abs(day1["max_cpu"] - 70.2) < 0.1, f"Day 1 max_cpu expected 70.2, got {day1['max_cpu']}"


def test_day3_max_cpu(report):
    """Day 3 max CPU should be 88.2."""
    day3 = report["daily"][2]
    assert abs(day3["max_cpu"] - 88.2) < 0.1, f"Day 3 max_cpu expected 88.2, got {day3['max_cpu']}"


def test_day1_total_requests(report):
    """Day 1 total requests should be 7040."""
    day1 = report["daily"][0]
    assert abs(day1["total_requests"] - 7040) < 50, f"Day 1 total_requests expected ~7040, got {day1['total_requests']}"


def test_day3_avg_memory(report):
    """Day 3 avg memory should be approximately 561.04 (within tolerance)."""
    day3 = report["daily"][2]
    assert abs(day3["avg_memory"] - 561.04) < 5.0, f"Day 3 avg_memory expected ~561.04, got {day3['avg_memory']}"


def test_trend_keys(report):
    """Trend must have cpu, memory, and requests keys."""
    required = {"cpu", "memory", "requests"}
    assert required.issubset(report["trend"].keys()), f"Missing trend keys: {required - report['trend'].keys()}"


def test_trend_values_valid(report):
    """Trend values must be one of increasing, decreasing, or stable."""
    valid = {"increasing", "decreasing", "stable"}
    for key, value in report["trend"].items():
        assert value in valid, f"Invalid trend value '{value}' for '{key}'"


def test_cpu_trend_increasing(report):
    """CPU trend should be increasing (day 3 avg_cpu >> day 1 avg_cpu)."""
    assert report["trend"]["cpu"] == "increasing", f"CPU trend expected 'increasing', got '{report['trend']['cpu']}'"


def test_memory_trend_increasing(report):
    """Memory trend should be increasing (day 3 avg_memory > day 1 avg_memory)."""
    assert report["trend"]["memory"] == "increasing", f"Memory trend expected 'increasing', got '{report['trend']['memory']}'"


def test_requests_trend_increasing(report):
    """Requests trend should be increasing (day 3 total > day 1 total)."""
    assert report["trend"]["requests"] == "increasing", f"Requests trend expected 'increasing', got '{report['trend']['requests']}'"


def test_avg_values_rounded(report):
    """avg_cpu and avg_memory should be rounded to 2 decimal places."""
    for entry in report["daily"]:
        avg_cpu_str = str(entry["avg_cpu"])
        if "." in avg_cpu_str:
            assert len(avg_cpu_str.split(".")[1]) <= 2, f"avg_cpu {entry['avg_cpu']} not rounded to 2 decimals"
        avg_mem_str = str(entry["avg_memory"])
        if "." in avg_mem_str:
            assert len(avg_mem_str.split(".")[1]) <= 2, f"avg_memory {entry['avg_memory']} not rounded to 2 decimals"
