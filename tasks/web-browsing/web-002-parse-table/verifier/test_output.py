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
