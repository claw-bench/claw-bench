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
