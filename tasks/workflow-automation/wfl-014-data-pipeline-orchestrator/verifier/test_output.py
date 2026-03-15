"""Verifier for wfl-014: Data Pipeline Orchestrator."""

import csv
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return request.config.getoption("--workspace")


@pytest.fixture
def output_data(workspace):
    path = Path(workspace) / "output.csv"
    assert path.exists(), "output.csv not found in workspace"
    with open(path) as f:
        reader = csv.DictReader(f)
        return list(reader)


@pytest.fixture
def output_headers(workspace):
    path = Path(workspace) / "output.csv"
    with open(path) as f:
        reader = csv.DictReader(f)
        return reader.fieldnames


def test_output_file_exists(workspace):
    assert (Path(workspace) / "output.csv").exists()


def test_correct_columns(output_headers):
    assert "region" in output_headers
    assert "sum_total_sales" in output_headers
    assert len(output_headers) == 2


def test_correct_row_count(output_data):
    assert len(output_data) == 3, f"Expected 3 regions, got {len(output_data)}"


def test_regions_present(output_data):
    regions = {row["region"] for row in output_data}
    assert regions == {"North", "South", "East"}


def test_north_total(output_data):
    north = [r for r in output_data if r["region"] == "North"][0]
    # North Widget: 5000 + 5500 + 5250 = 15750
    assert float(north["sum_total_sales"]) == 15750.0


def test_south_total(output_data):
    south = [r for r in output_data if r["region"] == "South"][0]
    # South Widget: 7500 + 8000 + 7000 = 22500
    assert float(south["sum_total_sales"]) == 22500.0


def test_east_total(output_data):
    east = [r for r in output_data if r["region"] == "East"][0]
    # East Widget: 6000 + 6500 + 6250 = 18750
    assert float(east["sum_total_sales"]) == 18750.0


def test_no_gadget_data(output_data):
    """Gadget rows should have been filtered out."""
    for row in output_data:
        assert "Gadget" not in str(row.values())
