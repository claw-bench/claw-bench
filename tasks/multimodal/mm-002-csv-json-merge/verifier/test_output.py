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
    path = workspace / "performance.json"
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
    path = workspace / "performance.json"
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
    path = workspace / "employees.csv"
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
