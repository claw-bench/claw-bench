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
