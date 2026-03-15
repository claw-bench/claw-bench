"""Verifier for data-009: Data Cleaning Pipeline."""

from pathlib import Path
import csv
import json
import re
import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def clean_rows(workspace):
    path = workspace / "clean_data.csv"
    assert path.exists(), "clean_data.csv not found"
    with open(path) as f:
        return list(csv.DictReader(f))


@pytest.fixture
def report(workspace):
    path = workspace / "cleaning_report.json"
    assert path.exists(), "cleaning_report.json not found"
    return json.loads(path.read_text())


def test_clean_file_exists(workspace):
    assert (workspace / "clean_data.csv").exists()


def test_report_file_exists(workspace):
    assert (workspace / "cleaning_report.json").exists()


def test_no_missing_ids(clean_rows):
    for row in clean_rows:
        assert row["id"].strip() != "", f"Found row with missing id"


def test_no_duplicate_ids(clean_rows):
    ids = [row["id"] for row in clean_rows]
    assert len(ids) == len(set(ids)), "Found duplicate ids in clean data"


def test_no_missing_salaries(clean_rows):
    for row in clean_rows:
        assert row["salary"].strip() != "", f"Found row with missing salary: id={row['id']}"


def test_emails_normalized(clean_rows):
    for row in clean_rows:
        email = row["email"]
        if email:
            assert email == email.lower().strip(), f"Email not normalized: {email}"


def test_phones_normalized(clean_rows):
    for row in clean_rows:
        phone = row["phone"]
        if phone:
            assert re.match(r"^\d{10}$", phone), f"Phone not in 10-digit format: {phone}"


def test_dates_normalized(clean_rows):
    for row in clean_rows:
        d = row["date_joined"]
        assert re.match(r"^\d{4}-\d{2}-\d{2}$", d), f"Date not in YYYY-MM-DD format: {d}"


def test_sorted_by_id(clean_rows):
    ids = [int(row["id"]) for row in clean_rows]
    assert ids == sorted(ids), "Rows not sorted by id"


def test_report_counts(report):
    assert report["duplicates_removed"] >= 3, f"Expected at least 3 duplicates removed, got {report['duplicates_removed']}"
    assert report["missing_values_filled"] >= 2, f"Expected at least 2 missing values filled, got {report['missing_values_filled']}"
    assert report["rows_dropped"] >= 1, f"Expected at least 1 row dropped, got {report['rows_dropped']}"
    assert report["total_clean_rows"] > 0, "No clean rows"
