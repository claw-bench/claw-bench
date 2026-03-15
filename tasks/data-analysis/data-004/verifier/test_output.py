"""Verifier for data-004: Pivot Table."""

from pathlib import Path
import csv
import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def pivot_rows(workspace):
    path = workspace / "pivot.csv"
    assert path.exists(), "pivot.csv not found in workspace"
    with open(path) as f:
        reader = csv.DictReader(f)
        return list(reader)


def test_pivot_file_exists(workspace):
    assert (workspace / "pivot.csv").exists()


def test_correct_row_count(pivot_rows):
    """4 months + 1 total row = 5 data rows."""
    assert len(pivot_rows) == 5, f"Expected 5 rows (4 months + total), got {len(pivot_rows)}"


def test_months_in_order(pivot_rows):
    month_rows = [r for r in pivot_rows if r["month"] != "Total"]
    months = [r["month"] for r in month_rows]
    assert months == sorted(months), f"Months not in chronological order: {months}"


def test_has_total_row(pivot_rows):
    total_rows = [r for r in pivot_rows if r["month"] == "Total"]
    assert len(total_rows) == 1, "Missing Total row"


def test_category_columns_present(workspace):
    path = workspace / "pivot.csv"
    header = path.read_text().strip().splitlines()[0]
    for cat in ['Entertainment', 'Food', 'Transport']:
        assert cat in header, f"Missing category column: {cat}"


def test_total_row_sums(pivot_rows):
    cats = [k for k in pivot_rows[0].keys() if k != "month"]
    month_rows = [r for r in pivot_rows if r["month"] != "Total"]
    total_row = [r for r in pivot_rows if r["month"] == "Total"][0]
    for cat in cats:
        expected = round(sum(float(r[cat]) for r in month_rows), 2)
        actual = round(float(total_row[cat]), 2)
        assert abs(actual - expected) < 0.02, f"Total for {cat}: expected {expected}, got {actual}"


def test_specific_sums(pivot_rows):
    expected = {"2025-01": {"Food": 376.93, "Transport": 401.85, "Entertainment": 376.53}, "2025-02": {"Food": 264.5, "Transport": 469.99, "Entertainment": 194.72}, "2025-03": {"Food": 198.23, "Transport": 265.86, "Entertainment": 300.26}, "2025-04": {"Food": 250.13, "Transport": 489.48, "Entertainment": 300.13}}
    month_rows = {r["month"]: r for r in pivot_rows if r["month"] != "Total"}
    for m, cats_dict in expected.items():
        assert m in month_rows, f"Missing month {m}"
        for cat, val in cats_dict.items():
            actual = round(float(month_rows[m][cat]), 2)
            assert abs(actual - val) < 0.02, f"{m}/{cat}: expected {val}, got {actual}"
