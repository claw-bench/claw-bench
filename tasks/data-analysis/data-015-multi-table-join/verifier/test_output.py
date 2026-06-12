"""Verifier for data-015: Multi-Table Join Analysis."""

import csv
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def summary(workspace):
    """Read and parse summary.csv."""
    path = workspace / "summary.csv"
    assert path.exists(), "summary.csv not found in workspace"
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def test_output_file_exists(workspace):
    """summary.csv must exist in the workspace."""
    assert (workspace / "summary.csv").exists()


def test_has_required_columns(summary):
    """summary.csv must have customer_name, region, category, total_revenue columns."""
    required = {"customer_name", "region", "category", "total_revenue"}
    assert required.issubset(summary[0].keys()), f"Missing columns: {required - summary[0].keys()}"


def test_row_count(summary):
    """There should be at least 5 rows (various customer-category combos)."""
    assert len(summary) >= 5, f"Expected at least 5 rows, got {len(summary)}"


def test_sorted_by_revenue_descending(summary):
    """Rows must be sorted by total_revenue descending."""
    revenues = [float(r["total_revenue"]) for r in summary]
    assert revenues == sorted(revenues, reverse=True), "Rows not sorted by total_revenue descending"


def test_alice_electronics_revenue(summary):
    """Alice Zhang Electronics revenue should be ~89.97 (3 * 29.99)."""
    for row in summary:
        if row["customer_name"] == "Alice Zhang" and row["category"] == "Electronics":
            assert abs(float(row["total_revenue"]) - 89.97) < 0.1
            return
    pytest.fail("Alice Zhang Electronics row not found")


def test_bob_electronics_revenue(summary):
    """Bob Smith Electronics revenue should be ~249.95 (5 * 49.99)."""
    for row in summary:
        if row["customer_name"] == "Bob Smith" and row["category"] == "Electronics":
            assert abs(float(row["total_revenue"]) - 249.95) < 0.1
            return
    pytest.fail("Bob Smith Electronics row not found")


def test_eve_electronics_revenue(summary):
    """Eve Brown Electronics revenue should be ~179.94 (6 * 29.99)."""
    for row in summary:
        if row["customer_name"] == "Eve Brown" and row["category"] == "Electronics":
            assert abs(float(row["total_revenue"]) - 179.94) < 0.1
            return
    pytest.fail("Eve Brown Electronics row not found")


def test_regions_present(summary):
    """All regions (East, West, North) should appear."""
    regions = {r["region"] for r in summary}
    assert "East" in regions
    assert "West" in regions
    assert "North" in regions


def test_total_revenue_rounded(summary):
    """All total_revenue values should be rounded to 2 decimal places."""
    for row in summary:
        val = row["total_revenue"]
        if "." in val:
            assert len(val.split(".")[1]) <= 2, f"total_revenue {val} not rounded to 2 decimals"


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
    path = workspace / "customers.csv"
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
