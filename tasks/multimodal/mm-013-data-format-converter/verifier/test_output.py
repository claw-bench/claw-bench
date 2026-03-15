"""Verifier for mm-013: Data Format Converter."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def output_data(workspace):
    path = workspace / "output.json"
    assert path.exists(), "output.json not found in workspace"
    return json.loads(path.read_text())


def test_output_file_exists(workspace):
    assert (workspace / "output.json").exists()


def test_valid_json(workspace):
    path = workspace / "output.json"
    try:
        json.loads(path.read_text())
    except json.JSONDecodeError as e:
        pytest.fail(f"output.json is not valid JSON: {e}")


def test_is_array(output_data):
    assert isinstance(output_data, list), "Output must be a JSON array"


def test_row_count(output_data):
    assert len(output_data) == 10, f"Expected 10 rows, got {len(output_data)}"


def test_field_names_renamed(output_data):
    expected_fields = {"employeeId", "fullName", "department", "annualSalary", "yearsExperience", "isManager"}
    for i, obj in enumerate(output_data):
        assert set(obj.keys()) == expected_fields, f"Row {i} has wrong fields: {set(obj.keys())}"


def test_no_original_column_names(output_data):
    original = {"emp_id", "emp_name", "dept", "salary", "years_exp", "is_manager"}
    for obj in output_data:
        for key in obj:
            assert key not in original, f"Found original column name '{key}' — should be renamed"


def test_employee_id_is_integer(output_data):
    for obj in output_data:
        assert isinstance(obj["employeeId"], int), f"employeeId must be int, got {type(obj['employeeId'])}"


def test_annual_salary_is_float(output_data):
    for obj in output_data:
        assert isinstance(obj["annualSalary"], (int, float)), \
            f"annualSalary must be numeric, got {type(obj['annualSalary'])}"


def test_years_experience_is_integer(output_data):
    for obj in output_data:
        assert isinstance(obj["yearsExperience"], int), \
            f"yearsExperience must be int, got {type(obj['yearsExperience'])}"


def test_is_manager_is_boolean(output_data):
    for obj in output_data:
        assert isinstance(obj["isManager"], bool), \
            f"isManager must be bool, got {type(obj['isManager'])}"


def test_full_name_is_string(output_data):
    for obj in output_data:
        assert isinstance(obj["fullName"], str), f"fullName must be string"


def test_first_row_values(output_data):
    first = output_data[0]
    assert first["employeeId"] == 101
    assert first["fullName"] == "Alice Chen"
    assert first["department"] == "Engineering"
    assert first["annualSalary"] == 95000.0
    assert first["yearsExperience"] == 8
    assert first["isManager"] is True


def test_last_row_values(output_data):
    last = output_data[9]
    assert last["employeeId"] == 110
    assert last["fullName"] == "Jack Wilson"
    assert last["department"] == "Sales"
    assert last["annualSalary"] == 82000.0
    assert last["yearsExperience"] == 9
    assert last["isManager"] is True


def test_boolean_false_values(output_data):
    bob = output_data[1]
    assert bob["isManager"] is False
    assert bob["fullName"] == "Bob Smith"


def test_specific_salary_values(output_data):
    salaries = [obj["annualSalary"] for obj in output_data]
    assert 105000.0 in salaries, "Carol's salary of 105000 must be present"
    assert 112000.0 in salaries, "Henry's salary of 112000 must be present"
