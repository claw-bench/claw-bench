"""Verifier for file-015: Complex Data Transformation Pipeline."""

import csv
import json
import re
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def clean_csv(workspace):
    """Read and parse the clean_data.csv file."""
    path = workspace / "clean_data.csv"
    assert path.exists(), "clean_data.csv not found in workspace"
    text = path.read_text().strip()
    lines = text.splitlines()
    reader = csv.DictReader(lines)
    return list(reader)


@pytest.fixture
def summary(workspace):
    """Read and parse the summary.json file."""
    path = workspace / "summary.json"
    assert path.exists(), "summary.json not found in workspace"
    return json.loads(path.read_text())


def test_clean_csv_exists(workspace):
    """clean_data.csv must exist in the workspace."""
    assert (workspace / "clean_data.csv").exists()


def test_summary_json_exists(workspace):
    """summary.json must exist in the workspace."""
    assert (workspace / "summary.json").exists()


def test_correct_row_count(clean_csv):
    """Cleaned data should have 22 rows (3 rows with empty fields removed)."""
    assert len(clean_csv) == 22, f"Expected 22 rows, got {len(clean_csv)}"


def test_no_empty_cells(clean_csv):
    """No cell in the cleaned CSV should be empty."""
    for i, row in enumerate(clean_csv):
        for key, value in row.items():
            assert value.strip() != "", (
                f"Empty cell found at row {i+1}, column '{key}'"
            )


def test_names_title_case(clean_csv):
    """All names should be in Title Case."""
    for row in clean_csv:
        name = row["name"]
        assert name == name.title(), (
            f"Name '{name}' is not Title Case, expected '{name.title()}'"
        )


def test_cities_title_case(clean_csv):
    """All cities should be in Title Case."""
    for row in clean_csv:
        city = row["city"]
        assert city == city.title(), (
            f"City '{city}' is not Title Case, expected '{city.title()}'"
        )


def test_dates_normalized(clean_csv):
    """All dates should be in YYYY-MM-DD format."""
    date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    for row in clean_csv:
        assert date_pattern.match(row["date"]), (
            f"Date '{row['date']}' is not in YYYY-MM-DD format"
        )


def test_has_total_column(clean_csv):
    """Cleaned CSV must have a 'total' column."""
    assert "total" in clean_csv[0], "Missing 'total' column in clean_data.csv"


def test_total_computed_correctly(clean_csv):
    """The total column should equal quantity * price."""
    for i, row in enumerate(clean_csv):
        quantity = int(row["quantity"])
        price = float(row["price"])
        total = float(row["total"])
        expected = round(quantity * price, 2)
        assert abs(total - expected) < 0.01, (
            f"Row {i+1}: total={total}, expected {quantity}*{price}={expected}"
        )


def test_summary_total_rows(summary):
    """Summary should report 22 total rows."""
    assert summary["total_rows"] == 22, (
        f"Expected total_rows=22, got {summary['total_rows']}"
    )


def test_summary_total_revenue(summary):
    """Summary total_revenue should be approximately 1938.06."""
    assert abs(summary["total_revenue"] - 1938.06) < 0.10, (
        f"Expected total_revenue~1938.06, got {summary['total_revenue']}"
    )


def test_summary_average_order(summary):
    """Summary average_order should be approximately 88.09."""
    assert abs(summary["average_order"] - 88.09) < 0.10, (
        f"Expected average_order~88.09, got {summary['average_order']}"
    )


def test_summary_cities(summary):
    """Summary cities list should contain the 4 unique cities, sorted."""
    expected_cities = ["Boston", "Chicago", "New York", "Seattle"]
    assert summary["cities"] == expected_cities, (
        f"Expected cities {expected_cities}, got {summary['cities']}"
    )


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
    path = workspace / "summary.json"
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
    path = workspace / "summary.json"
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
    path = workspace / "raw_data.csv"
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
