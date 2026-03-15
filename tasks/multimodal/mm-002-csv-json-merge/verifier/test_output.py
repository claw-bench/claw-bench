"""Verifier for mm-002: CSV and JSON Merge."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def combined(workspace):
    path = workspace / "combined.json"
    assert path.exists(), "combined.json not found in workspace"
    with open(path) as f:
        return json.load(f)


def test_output_file_exists(workspace):
    assert (workspace / "combined.json").exists()


def test_valid_json(workspace):
    path = workspace / "combined.json"
    try:
        with open(path) as f:
            json.load(f)
    except json.JSONDecodeError as e:
        pytest.fail(f"combined.json is not valid JSON: {e}")


def test_correct_employee_count(combined):
    assert len(combined) == 8, f"Expected 8 employees, got {len(combined)}"


def test_sorted_by_employee_id(combined):
    ids = [e["employee_id"] for e in combined]
    assert ids == sorted(ids), "Employees must be sorted by employee_id"


def test_all_employee_ids_present(combined):
    ids = {e["employee_id"] for e in combined}
    expected = {"E001", "E002", "E003", "E004", "E005", "E006", "E007", "E008"}
    assert ids == expected


def test_csv_fields_present(combined):
    required = {"employee_id", "first_name", "last_name", "department", "hire_date"}
    for emp in combined:
        assert required.issubset(emp.keys()), f"Missing CSV fields in {emp.get('employee_id')}"


def test_performance_reviews_field_present(combined):
    for emp in combined:
        assert "performance_reviews" in emp, f"Missing performance_reviews for {emp['employee_id']}"
        assert isinstance(emp["performance_reviews"], list)


def test_employee_with_no_reviews(combined):
    """E006 (Frank Lee) has no reviews."""
    e006 = next(e for e in combined if e["employee_id"] == "E006")
    assert e006["performance_reviews"] == []


def test_employee_with_multiple_reviews(combined):
    """E001 should have 2 reviews."""
    e001 = next(e for e in combined if e["employee_id"] == "E001")
    assert len(e001["performance_reviews"]) == 2


def test_review_fields(combined):
    """Reviews should have review_year, rating, goals_met, reviewer but NOT employee_id."""
    e001 = next(e for e in combined if e["employee_id"] == "E001")
    for review in e001["performance_reviews"]:
        assert "review_year" in review
        assert "rating" in review
        assert "goals_met" in review
        assert "reviewer" in review
        assert "employee_id" not in review, "employee_id should not be in review sub-objects"


def test_rating_is_number(combined):
    e005 = next(e for e in combined if e["employee_id"] == "E005")
    for review in e005["performance_reviews"]:
        assert isinstance(review["rating"], (int, float))


def test_goals_met_is_boolean(combined):
    e003 = next(e for e in combined if e["employee_id"] == "E003")
    for review in e003["performance_reviews"]:
        assert isinstance(review["goals_met"], bool)


def test_specific_data_alice(combined):
    e001 = next(e for e in combined if e["employee_id"] == "E001")
    assert e001["first_name"] == "Alice"
    assert e001["last_name"] == "Johnson"
    assert e001["department"] == "Engineering"
    ratings = sorted([r["rating"] for r in e001["performance_reviews"]])
    assert ratings == [4.5, 4.7]


def test_specific_data_grace(combined):
    e007 = next(e for e in combined if e["employee_id"] == "E007")
    assert e007["first_name"] == "Grace"
    assert e007["department"] == "Sales"
    assert len(e007["performance_reviews"]) == 2


def test_total_reviews_count(combined):
    """Total number of reviews across all employees should be 11."""
    total = sum(len(e["performance_reviews"]) for e in combined)
    assert total == 11, f"Expected 11 total reviews, got {total}"
