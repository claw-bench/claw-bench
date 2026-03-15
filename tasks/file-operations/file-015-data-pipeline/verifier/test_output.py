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
