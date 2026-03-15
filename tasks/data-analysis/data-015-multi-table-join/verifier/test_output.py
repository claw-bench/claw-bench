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
