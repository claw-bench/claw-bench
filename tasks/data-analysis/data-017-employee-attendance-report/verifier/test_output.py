"""Verifier for data-017: Employee Attendance Analysis."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def report(workspace):
    """Read and parse attendance_report.json."""
    path = workspace / "attendance_report.json"
    assert path.exists(), "attendance_report.json not found in workspace"
    return json.loads(path.read_text())


def _get_employee(report, name):
    """Helper to find an employee entry by name."""
    matches = [e for e in report["employees"] if e["name"] == name]
    assert len(matches) == 1, f"Expected exactly one entry for {name}"
    return matches[0]


def test_output_file_exists(workspace):
    """attendance_report.json must exist in the workspace."""
    assert (workspace / "attendance_report.json").exists()


def test_top_level_keys(report):
    """Report must contain all required top-level keys."""
    required = {"period", "employees", "team_avg_hours", "most_punctual", "total_late_arrivals"}
    assert required.issubset(report.keys()), f"Missing keys: {required - report.keys()}"


def test_period(report):
    """Period must be 2026-03-09 to 2026-03-13."""
    assert report["period"] == "2026-03-09 to 2026-03-13"


def test_employee_count(report):
    """There should be exactly 3 employees."""
    assert len(report["employees"]) == 3


def test_employee_entry_structure(report):
    """Each employee entry must have all required fields."""
    required = {"name", "total_hours", "avg_hours_per_day", "late_days", "late_dates", "punctuality_rate"}
    for emp in report["employees"]:
        assert required.issubset(emp.keys()), (
            f"{emp.get('name', '?')} missing keys: {required - emp.keys()}"
        )


def test_alice_total_hours(report):
    """Alice total_hours should be approximately 41.75."""
    alice = _get_employee(report, "Alice")
    assert abs(alice["total_hours"] - 41.75) < 0.1, (
        f"Alice total_hours expected ~41.75, got {alice['total_hours']}"
    )


def test_alice_late_days(report):
    """Alice should have 2 late days."""
    alice = _get_employee(report, "Alice")
    assert alice["late_days"] == 2


def test_alice_late_dates(report):
    """Alice should be late on 2026-03-10 and 2026-03-12."""
    alice = _get_employee(report, "Alice")
    assert "2026-03-10" in alice["late_dates"]
    assert "2026-03-12" in alice["late_dates"]


def test_alice_punctuality(report):
    """Alice punctuality_rate should be 0.60."""
    alice = _get_employee(report, "Alice")
    assert abs(alice["punctuality_rate"] - 0.60) < 0.01


def test_bob_total_hours(report):
    """Bob total_hours should be approximately 40.58."""
    bob = _get_employee(report, "Bob")
    assert abs(bob["total_hours"] - 40.58) < 0.1, (
        f"Bob total_hours expected ~40.58, got {bob['total_hours']}"
    )


def test_bob_late_days(report):
    """Bob should have 2 late days."""
    bob = _get_employee(report, "Bob")
    assert bob["late_days"] == 2


def test_bob_late_dates(report):
    """Bob should be late on 2026-03-10 and 2026-03-12."""
    bob = _get_employee(report, "Bob")
    assert "2026-03-10" in bob["late_dates"]
    assert "2026-03-12" in bob["late_dates"]


def test_bob_punctuality(report):
    """Bob punctuality_rate should be 0.60."""
    bob = _get_employee(report, "Bob")
    assert abs(bob["punctuality_rate"] - 0.60) < 0.01


def test_carol_total_hours(report):
    """Carol total_hours should be approximately 42.33."""
    carol = _get_employee(report, "Carol")
    assert abs(carol["total_hours"] - 42.33) < 0.1, (
        f"Carol total_hours expected ~42.33, got {carol['total_hours']}"
    )


def test_carol_late_days(report):
    """Carol should have 0 late days."""
    carol = _get_employee(report, "Carol")
    assert carol["late_days"] == 0


def test_carol_punctuality(report):
    """Carol punctuality_rate should be 1.0."""
    carol = _get_employee(report, "Carol")
    assert abs(carol["punctuality_rate"] - 1.0) < 0.01


def test_most_punctual(report):
    """Most punctual employee should be Carol."""
    assert report["most_punctual"] == "Carol"


def test_total_late_arrivals(report):
    """Total late arrivals should be 4."""
    assert report["total_late_arrivals"] == 4


def test_team_avg_hours(report):
    """Team average hours should be approximately 41.55."""
    assert abs(report["team_avg_hours"] - 41.55) < 0.1, (
        f"team_avg_hours expected ~41.55, got {report['team_avg_hours']}"
    )


def test_employees_sorted_alphabetically(report):
    """Employees list should be sorted by name."""
    names = [e["name"] for e in report["employees"]]
    assert names == sorted(names), f"Employees not sorted: {names}"
