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


# ── Enhanced checks (auto-generated) ────────────────────────────────────────

@pytest.mark.weight(1)
def test_no_placeholder_values(workspace):
    """Output files must not contain placeholder/TODO markers."""
    placeholders = ["PLACEHOLDER", "CHANGEME", "your_"]
    for f in workspace.iterdir():
        if f.is_file() and f.suffix in (".json", ".csv", ".txt", ".md", ".py", ".yaml", ".yml", ".html", ".xml"):
            content = f.read_text(errors="replace")
            for p in placeholders:
                assert p not in content, f"Placeholder '{p}' found in {f.name}"

@pytest.mark.weight(2)
def test_no_empty_critical_fields(workspace):
    """JSON output must not have empty-string or null values in top-level fields."""
    import json
    path = workspace / "schema.json"
    if not path.exists():
        pytest.skip("output file not found")
    data = json.loads(path.read_text())
    items = data if isinstance(data, list) else [data]
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        for k, v in item.items():
            assert v is not None, f"Item {i}: field '{k}' is null"
            if isinstance(v, str):
                assert v.strip() != "", f"Item {i}: field '{k}' is empty string"

@pytest.mark.weight(1)
def test_encoding_valid(workspace):
    """All text output files must be valid UTF-8."""
    for f in workspace.iterdir():
        if f.is_file() and f.suffix in (".json", ".csv", ".txt", ".md", ".py", ".yaml", ".yml", ".html"):
            try:
                f.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                pytest.fail(f"{f.name} contains invalid UTF-8 encoding")

@pytest.mark.weight(1)
def test_consistent_key_naming(workspace):
    """JSON keys should use a consistent naming convention."""
    import json, re
    path = workspace / "schema.json"
    if not path.exists():
        pytest.skip("output file not found")
    data = json.loads(path.read_text())
    items = data if isinstance(data, list) else [data]
    all_keys = set()
    for item in items:
        if isinstance(item, dict):
            all_keys.update(item.keys())
    if len(all_keys) < 2:
        return
    snake = sum(1 for k in all_keys if re.match(r'^[a-z][a-z0-9_]*$', k))
    camel = sum(1 for k in all_keys if re.match(r'^[a-z][a-zA-Z0-9]*$', k) and not re.match(r'^[a-z][a-z0-9_]*$', k))
    pascal = sum(1 for k in all_keys if re.match(r'^[A-Z][a-zA-Z0-9]*$', k))
    dominant = max(snake, camel, pascal)
    consistency = dominant / len(all_keys) if all_keys else 1
    assert consistency >= 0.7, f"Key naming inconsistent: {snake} snake, {camel} camel, {pascal} pascal out of {len(all_keys)} keys"

@pytest.mark.weight(1)
def test_no_duplicate_entries(workspace):
    """Output should not contain exact duplicate rows/objects."""
    import json
    path = workspace / "input.csv"
    if not path.exists():
        pytest.skip("output file not found")
    text = path.read_text().strip()
    if path.suffix == ".json":
        data = json.loads(text)
        if isinstance(data, list):
            serialized = [json.dumps(item, sort_keys=True) for item in data]
            dupes = len(serialized) - len(set(serialized))
            assert dupes == 0, f"Found {dupes} duplicate entries in {path.name}"
    elif path.suffix == ".csv":
        lines_list = text.splitlines()
        if len(lines_list) > 1:
            data_lines = lines_list[1:]
            dupes = len(data_lines) - len(set(data_lines))
            assert dupes == 0, f"Found {dupes} duplicate rows in {path.name}"

@pytest.mark.weight(1)
def test_no_extraneous_files(workspace):
    """Workspace should not contain debug/temp files."""
    bad_patterns = [".DS_Store", "Thumbs.db", ".log", ".bak", ".tmp"]
    for f in workspace.rglob("*"):
        if f.is_file():
            for pat in bad_patterns:
                assert pat not in f.name, f"Extraneous file found: {f.name}"

@pytest.mark.weight(1)
def test_output_not_excessively_large(workspace):
    """Output files should be reasonably sized (< 5MB each)."""
    for f in workspace.iterdir():
        if f.is_file() and f.suffix in (".json", ".csv", ".txt", ".md", ".py", ".yaml", ".yml", ".html"):
            size_mb = f.stat().st_size / (1024 * 1024)
            assert size_mb < 5, f"{f.name} is {size_mb:.1f}MB, exceeds 5MB limit"
