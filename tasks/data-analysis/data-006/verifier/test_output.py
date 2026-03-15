"""Verifier for data-006: Time Series Aggregation."""

from pathlib import Path
import csv
import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def weekly_rows(workspace):
    path = workspace / "weekly.csv"
    assert path.exists(), "weekly.csv not found"
    with open(path) as f:
        return list(csv.DictReader(f))


@pytest.fixture
def monthly_rows(workspace):
    path = workspace / "monthly.csv"
    assert path.exists(), "monthly.csv not found"
    with open(path) as f:
        return list(csv.DictReader(f))


def test_weekly_file_exists(workspace):
    assert (workspace / "weekly.csv").exists()


def test_monthly_file_exists(workspace):
    assert (workspace / "monthly.csv").exists()


def test_weekly_count(weekly_rows):
    assert len(weekly_rows) == 14, f"Expected 14 weeks, got {len(weekly_rows)}"


def test_monthly_count(monthly_rows):
    assert len(monthly_rows) == 3, f"Expected 3 months, got {len(monthly_rows)}"


def test_weekly_sums_match_total(weekly_rows):
    total = round(sum(float(r["total_amount"]) for r in weekly_rows), 2)
    assert abs(total - 24959.7) < 0.1, f"Weekly sums {total} != expected total 24959.7"


def test_monthly_sums_match_total(monthly_rows):
    total = round(sum(float(r["total_amount"]) for r in monthly_rows), 2)
    assert abs(total - 24959.7) < 0.1, f"Monthly sums {total} != expected total 24959.7"


def test_weekly_sorted(weekly_rows):
    weeks = [r["week"] for r in weekly_rows]
    assert weeks == sorted(weeks), "Weekly rows not in chronological order"


def test_monthly_sorted(monthly_rows):
    months = [r["month"] for r in monthly_rows]
    assert months == sorted(months), "Monthly rows not in chronological order"
