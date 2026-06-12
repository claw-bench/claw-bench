"""Verifier for web-002: Parse HTML Table."""

import csv
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def table_data(workspace):
    path = workspace / "table_data.csv"
    assert path.exists(), "table_data.csv not found"
    with open(path) as f:
        reader = csv.reader(f)
        return list(reader)


def test_output_file_exists(workspace):
    assert (workspace / "table_data.csv").exists()


def test_has_header_row(table_data):
    headers = table_data[0]
    assert "Region" in headers
    assert "Product" in headers
    assert "Total" in headers


def test_correct_column_count(table_data):
    for row in table_data:
        assert len(row) == 6, f"Expected 6 columns, got {len(row)}: {row}"


def test_correct_row_count(table_data):
    """8 data rows + 1 header = 9 total."""
    assert len(table_data) == 9


def test_data_rows_count(table_data):
    data_rows = table_data[1:]
    assert len(data_rows) == 8


def test_north_america_widget_a(table_data):
    row = [r for r in table_data[1:] if r[0] == "North America" and r[1] == "Widget A"]
    assert len(row) == 1
    assert row[0][2] == "15000"
    assert row[0][5] == "55000"


def test_europe_present(table_data):
    regions = [r[0] for r in table_data[1:]]
    assert "Europe" in regions


def test_asia_pacific_present(table_data):
    regions = [r[0] for r in table_data[1:]]
    assert "Asia Pacific" in regions


def test_latin_america_widget_b(table_data):
    row = [r for r in table_data[1:] if r[0] == "Latin America" and r[1] == "Widget B"]
    assert len(row) == 1
    assert row[0][5] == "6200"


def test_all_regions_present(table_data):
    regions = set(r[0] for r in table_data[1:])
    assert regions == {"North America", "Europe", "Asia Pacific", "Latin America"}


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
    path = workspace / "table_data.csv"
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
