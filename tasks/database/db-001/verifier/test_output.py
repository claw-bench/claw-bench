"""Verifier for db-001: Basic SQL Query."""

import json
import sqlite3
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def db_connection(workspace):
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    schema_path = workspace / "database.sql"
    assert schema_path.exists(), "database.sql not found in workspace"
    conn.executescript(schema_path.read_text())
    yield conn
    conn.close()


@pytest.fixture
def query_sql(workspace):
    path = workspace / "query.sql"
    assert path.exists(), "query.sql not found in workspace"
    return path.read_text().strip()


@pytest.fixture
def results_json(workspace):
    path = workspace / "results.json"
    assert path.exists(), "results.json not found in workspace"
    return json.loads(path.read_text())


@pytest.fixture
def expected_rows(db_connection):
    rows = db_connection.execute(
        "SELECT * FROM employees "
        "WHERE department = 'Engineering' AND salary > 80000 "
        "ORDER BY salary DESC"
    ).fetchall()
    return [dict(r) for r in rows]


@pytest.fixture
def query_result_rows(db_connection, query_sql):
    rows = db_connection.execute(query_sql).fetchall()
    return [dict(r) for r in rows]


# ── Core checks (weight 3) ──────────────────────────────────────────────────

@pytest.mark.weight(3)
def test_query_file_exists(workspace):
    """query.sql must exist."""
    assert (workspace / "query.sql").exists(), "query.sql not found"


@pytest.mark.weight(3)
def test_results_file_exists(workspace):
    """results.json must exist."""
    assert (workspace / "results.json").exists(), "results.json not found"


@pytest.mark.weight(3)
def test_query_is_select(query_sql):
    """Query must be a SELECT statement."""
    normalized = query_sql.upper().lstrip()
    assert normalized.startswith("SELECT"), "Query must be a SELECT statement"


@pytest.mark.weight(3)
def test_query_executes(db_connection, query_sql):
    """Query must execute without errors against the schema."""
    try:
        db_connection.execute(query_sql)
    except Exception as e:
        pytest.fail(f"Query execution failed: {e}")


@pytest.mark.weight(3)
def test_correct_row_count(query_result_rows):
    """Query should return exactly 3 employees."""
    assert len(query_result_rows) == 4, (
        f"Expected 4 rows, got {len(query_result_rows)}"
    )


@pytest.mark.weight(3)
def test_all_engineering(query_result_rows):
    """All returned employees must be in Engineering department."""
    for row in query_result_rows:
        assert row["department"] == "Engineering", (
            f"Row {row.get('name', '?')} is in {row['department']}, not Engineering"
        )


@pytest.mark.weight(3)
def test_all_above_salary_threshold(query_result_rows):
    """All returned salaries must be greater than 80000."""
    for row in query_result_rows:
        assert row["salary"] > 80000, (
            f"{row.get('name', '?')} has salary {row['salary']} <= 80000"
        )


@pytest.mark.weight(3)
def test_correct_employees_returned(query_result_rows):
    """Must return all Engineering employees with salary > 80000."""
    names = {row["name"] for row in query_result_rows}
    expected = {"Alice Chen", "Carol White", "Eva Johnson", "Henry Brown"}
    assert names == expected, f"Expected {expected}, got {names}"


@pytest.mark.weight(3)
def test_results_json_valid(results_json):
    """results.json must be a list of objects."""
    assert isinstance(results_json, list), "results.json must be a JSON array"
    for item in results_json:
        assert isinstance(item, dict), "Each result must be a JSON object"


@pytest.mark.weight(3)
def test_results_json_row_count(results_json):
    """results.json must contain exactly 4 rows."""
    assert len(results_json) == 4, f"Expected 4 results, got {len(results_json)}"


@pytest.mark.weight(3)
def test_results_json_has_correct_names(results_json):
    """results.json must contain the correct employee names."""
    names = {r.get("name") for r in results_json}
    expected = {"Alice Chen", "Carol White", "Eva Johnson", "Henry Brown"}
    assert names == expected, f"Expected {expected}, got {names}"


# ── Bonus checks (weight 1) ──────────────────────────────────────────────────

@pytest.mark.weight(1)
def test_results_sorted_by_salary_desc(results_json):
    """Results should be sorted by salary descending."""
    salaries = [r["salary"] for r in results_json]
    assert salaries == sorted(salaries, reverse=True), (
        f"Results not sorted by salary desc: {salaries}"
    )


@pytest.mark.weight(1)
def test_results_have_all_columns(results_json):
    """Each result object should have all 5 columns."""
    required = {"id", "name", "department", "salary", "hire_date"}
    for row in results_json:
        assert required.issubset(row.keys()), (
            f"Missing columns: {required - set(row.keys())}"
        )


@pytest.mark.weight(1)
def test_query_references_department(query_sql):
    """Query should filter by department."""
    upper = query_sql.upper()
    assert "DEPARTMENT" in upper, "Query should reference department column"


@pytest.mark.weight(1)
def test_query_references_salary(query_sql):
    """Query should filter by salary."""
    upper = query_sql.upper()
    assert "SALARY" in upper, "Query should reference salary column"


@pytest.mark.weight(1)
def test_excludes_frank_liu(query_result_rows):
    """Frank Liu (salary=78000) must NOT be included."""
    names = {row["name"] for row in query_result_rows}
    assert "Frank Liu" not in names, "Frank Liu (78000) should be excluded"


@pytest.mark.weight(1)
def test_excludes_jack_wilson(query_result_rows):
    """Jack Wilson (salary=75000) must NOT be included."""
    names = {row["name"] for row in query_result_rows}
    assert "Jack Wilson" not in names, "Jack Wilson (75000) should be excluded"


@pytest.mark.weight(1)
def test_no_extraneous_files(workspace):
    """Workspace should not contain debug/temp files."""
    bad_patterns = [".DS_Store", ".bak", ".tmp"]
    for f in workspace.iterdir():
        if f.is_file():
            for pat in bad_patterns:
                assert pat not in f.name, f"Extraneous file found: {f.name}"


@pytest.mark.weight(1)
def test_encoding_valid(workspace):
    """All text output files must be valid UTF-8."""
    for f in workspace.iterdir():
        if f.is_file() and f.suffix in (".sql", ".json"):
            try:
                f.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                pytest.fail(f"{f.name} contains invalid UTF-8 encoding")
