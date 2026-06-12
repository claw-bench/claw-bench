"""Verifier for data-006: Time Series Aggregation."""

from pathlib import Path
import csv
import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def weekly_rows(workspace):
    path = workspace / "weekly.csv"
    assert path.exists(), "weekly.csv not found"
    with open(path) as f:
        return list(csv.DictReader(f))


@pytest.fixture
def monthly_rows(workspace):
    path = workspace / "monthly.csv"
    assert path.exists(), "monthly.csv not found"
    with open(path) as f:
        return list(csv.DictReader(f))


def test_weekly_file_exists(workspace):
    assert (workspace / "weekly.csv").exists()


def test_monthly_file_exists(workspace):
    assert (workspace / "monthly.csv").exists()


def test_weekly_count(weekly_rows):
    assert len(weekly_rows) == 14, f"Expected 14 weeks, got {len(weekly_rows)}"


def test_monthly_count(monthly_rows):
    assert len(monthly_rows) == 3, f"Expected 3 months, got {len(monthly_rows)}"


def test_weekly_sums_match_total(weekly_rows):
    total = round(sum(float(r["total_amount"]) for r in weekly_rows), 2)
    assert abs(total - 24959.7) < 0.1, f"Weekly sums {total} != expected total 24959.7"


def test_monthly_sums_match_total(monthly_rows):
    total = round(sum(float(r["total_amount"]) for r in monthly_rows), 2)
    assert abs(total - 24959.7) < 0.1, f"Monthly sums {total} != expected total 24959.7"


def test_weekly_sorted(weekly_rows):
    weeks = [r["week"] for r in weekly_rows]
    assert weeks == sorted(weeks), "Weekly rows not in chronological order"


def test_monthly_sorted(monthly_rows):
    months = [r["month"] for r in monthly_rows]
    assert months == sorted(months), "Monthly rows not in chronological order"


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
def test_no_duplicate_entries(workspace):
    """Output should not contain exact duplicate rows/objects."""
    import json
    path = workspace / "daily_sales.csv"
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

@pytest.mark.weight(2)
def test_json_parseable_if_present(workspace):
    """Any .json files in workspace must be valid JSON."""
    import json
    for f in workspace.iterdir():
        if f.is_file() and f.suffix == ".json":
            try:
                json.loads(f.read_text())
            except json.JSONDecodeError:
                pytest.fail(f"{f.name} is not valid JSON")
