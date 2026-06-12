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
    path = workspace / "attendance_report.json"
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
    path = workspace / "attendance_report.json"
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
    path = workspace / "attendance.csv"
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
