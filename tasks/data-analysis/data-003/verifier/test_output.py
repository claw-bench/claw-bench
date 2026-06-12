"""Verifier for data-003: Group and Aggregate Sales Data."""

from pathlib import Path
import csv
import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def summary_rows(workspace):
    path = workspace / "summary.csv"
    assert path.exists(), "summary.csv not found in workspace"
    with open(path) as f:
        reader = csv.DictReader(f)
        return list(reader)


def test_summary_file_exists(workspace):
    assert (workspace / "summary.csv").exists()


def test_correct_category_count(summary_rows):
    assert len(summary_rows) == 4, f"Expected 4 categories, got {len(summary_rows)}"


def test_correct_categories(summary_rows):
    cats = [row["category"] for row in summary_rows]
    expected = ['Electronics', 'Books', 'Food', 'Clothing']
    assert set(cats) == set(expected), f"Expected categories {expected}, got {cats}"


def test_correct_totals(summary_rows):
    expected = {'Electronics': 1029, 'Books': 818, 'Food': 817, 'Clothing': 543}
    for row in summary_rows:
        cat = row["category"]
        total = int(row["total_amount"])
        assert total == expected[cat], f"Category {cat}: expected {expected[cat]}, got {total}"


def test_sorted_descending(summary_rows):
    amounts = [int(row["total_amount"]) for row in summary_rows]
    assert amounts == sorted(amounts, reverse=True), "Results not sorted by total_amount descending"


def test_header_columns(workspace):
    path = workspace / "summary.csv"
    header = path.read_text().strip().splitlines()[0]
    assert "category" in header and "total_amount" in header


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
    path = workspace / "sales.csv"
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
