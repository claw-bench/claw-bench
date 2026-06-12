"""Verifier for data-002: Sort and Filter CSV Data."""

from pathlib import Path
import csv
import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def filtered_rows(workspace):
    path = workspace / "filtered.csv"
    assert path.exists(), "filtered.csv not found in workspace"
    with open(path) as f:
        reader = csv.DictReader(f)
        return list(reader)


def test_filtered_file_exists(workspace):
    assert (workspace / "filtered.csv").exists()


def test_correct_row_count(filtered_rows):
    assert len(filtered_rows) == 13, f"Expected 13 rows, got {len(filtered_rows)}"


def test_all_ages_above_25(filtered_rows):
    for row in filtered_rows:
        assert int(row["age"]) > 25, f"Found row with age <= 25: {row}"


def test_sorted_by_name(filtered_rows):
    names = [row["name"] for row in filtered_rows]
    assert names == sorted(names), "Rows are not sorted alphabetically by name"


def test_header_preserved(workspace):
    path = workspace / "filtered.csv"
    first_line = path.read_text().strip().splitlines()[0]
    assert "name" in first_line and "age" in first_line and "city" in first_line and "score" in first_line


def test_expected_names_present(filtered_rows):
    names = [row["name"] for row in filtered_rows]
    expected = ['Alice', 'Charlie', 'Eve', 'Grace', 'Hank', 'Jack', 'Kate', 'Leo', 'Nick', 'Paul', 'Rita', 'Sam', 'Tina']
    assert names == expected, f"Expected names {expected}, got {names}"


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
    path = workspace / "people.csv"
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
