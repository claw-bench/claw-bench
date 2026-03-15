"""Verifier for file-002: Convert CSV to JSON."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def output_json(workspace):
    """Read and parse the generated output.json."""
    path = workspace / "output.json"
    assert path.exists(), "output.json not found in workspace"
    text = path.read_text().strip()
    return json.loads(text)


def test_output_file_exists(workspace):
    """output.json must exist in the workspace."""
    assert (workspace / "output.json").exists()


def test_valid_json(workspace):
    """output.json must contain valid JSON."""
    path = workspace / "output.json"
    text = path.read_text().strip()
    try:
        json.loads(text)
    except json.JSONDecodeError:
        pytest.fail("output.json is not valid JSON")


def test_is_array(output_json):
    """The top-level JSON value must be an array."""
    assert isinstance(output_json, list), "Expected a JSON array"


def test_correct_row_count(output_json):
    """The array must contain exactly 6 objects (one per CSV data row)."""
    assert len(output_json) == 6, f"Expected 6 rows, got {len(output_json)}"


def test_correct_keys(output_json):
    """Each object must have the keys: Name, Email, Department, Salary."""
    expected_keys = {"Name", "Email", "Department", "Salary"}
    for i, obj in enumerate(output_json):
        assert set(obj.keys()) == expected_keys, (
            f"Row {i} has incorrect keys: {set(obj.keys())}"
        )


def test_contains_all_names(output_json):
    """All six employee names must be present."""
    names = [obj["Name"] for obj in output_json]
    for expected in [
        "Alice Johnson",
        "Bob Smith",
        "Carol Williams",
        "David Brown",
        "Eva Martinez",
        "Frank Lee",
    ]:
        assert expected in names, f"Missing name: {expected}"


def test_contains_all_emails(output_json):
    """All six email addresses must be present."""
    emails = [obj["Email"] for obj in output_json]
    for expected in [
        "alice.johnson@example.com",
        "bob.smith@example.com",
        "carol.williams@example.com",
        "david.brown@example.com",
        "eva.martinez@example.com",
        "frank.lee@example.com",
    ]:
        assert expected in emails, f"Missing email: {expected}"


def test_contains_all_departments(output_json):
    """All department values must be present."""
    departments = [obj["Department"] for obj in output_json]
    assert "Engineering" in departments
    assert "Marketing" in departments
    assert "Sales" in departments
    assert "Human Resources" in departments
