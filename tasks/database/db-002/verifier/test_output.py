"""Verifier for db-002: Multi-Table JOIN with Aggregation."""

import json
import sqlite3
from pathlib import Path

import pytest


EXPECTED_RESULTS = [
    {"customer_name": "Eva Garcia", "city": "Chicago", "total_spend": 870.00},
    {"customer_name": "David Lee", "city": "San Francisco", "total_spend": 825.50},
    {"customer_name": "Alice Wang", "city": "New York", "total_spend": 755.50},
    {"customer_name": "Bob Smith", "city": "Chicago", "total_spend": 730.25},
    {"customer_name": "Carol Jones", "city": "New York", "total_spend": 660.00},
]


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def db_connection(workspace):
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    schema_path = workspace / "schema.sql"
    assert schema_path.exists(), "schema.sql not found in workspace"
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
def query_result_rows(db_connection, query_sql):
    rows = db_connection.execute(query_sql).fetchall()
    return [dict(r) for r in rows]


# ── Core checks (weight 3) ──────────────────────────────────────────────────

@pytest.mark.weight(3)
def test_query_file_exists(workspace):
    """query.sql must exist."""
    assert (workspace / "query.sql").exists()


@pytest.mark.weight(3)
def test_results_file_exists(workspace):
    """results.json must exist."""
    assert (workspace / "results.json").exists()


@pytest.mark.weight(3)
def test_query_executes(db_connection, query_sql):
    """Query must execute without errors."""
    try:
        db_connection.execute(query_sql)
    except Exception as e:
        pytest.fail(f"Query execution failed: {e}")


@pytest.mark.weight(3)
def test_query_uses_join(query_sql):
    """Query must use a JOIN."""
    upper = query_sql.upper()
    assert "JOIN" in upper, "Query must use a JOIN"


@pytest.mark.weight(3)
def test_query_uses_group_by(query_sql):
    """Query must use GROUP BY."""
    upper = query_sql.upper()
    assert "GROUP BY" in upper, "Query must use GROUP BY for aggregation"


@pytest.mark.weight(3)
def test_query_uses_sum(query_sql):
    """Query must use SUM for aggregation."""
    upper = query_sql.upper()
    assert "SUM" in upper, "Query must use SUM to compute total spend"


@pytest.mark.weight(3)
def test_correct_row_count(query_result_rows):
    """Query should return exactly 5 customers."""
    assert len(query_result_rows) == 5, (
        f"Expected 5 rows, got {len(query_result_rows)}"
    )


@pytest.mark.weight(3)
def test_result_columns(query_result_rows):
    """Each row must have customer_name, city, and total_spend columns."""
    required = {"customer_name", "city", "total_spend"}
    for row in query_result_rows:
        keys_lower = {k.lower() for k in row.keys()}
        assert required.issubset(keys_lower), (
            f"Missing columns: {required - keys_lower}"
        )


@pytest.mark.weight(3)
def test_total_spend_alice(query_result_rows):
    """Alice Wang's total spend should be 755.50."""
    for row in query_result_rows:
        if row.get("customer_name") == "Alice Wang":
            assert abs(row["total_spend"] - 755.50) < 0.01, (
                f"Alice Wang's total_spend is {row['total_spend']}, expected 755.50"
            )
            return
    pytest.fail("Alice Wang not found in results")


@pytest.mark.weight(3)
def test_total_spend_bob(query_result_rows):
    """Bob Smith's total spend should be 730.25."""
    for row in query_result_rows:
        if row.get("customer_name") == "Bob Smith":
            assert abs(row["total_spend"] - 730.25) < 0.01, (
                f"Bob Smith's total_spend is {row['total_spend']}, expected 730.25"
            )
            return
    pytest.fail("Bob Smith not found in results")


@pytest.mark.weight(3)
def test_total_spend_eva(query_result_rows):
    """Eva Garcia's total spend should be 870.00."""
    for row in query_result_rows:
        if row.get("customer_name") == "Eva Garcia":
            assert abs(row["total_spend"] - 870.00) < 0.01, (
                f"Eva Garcia's total_spend is {row['total_spend']}, expected 870.00"
            )
            return
    pytest.fail("Eva Garcia not found in results")


# ── Bonus checks (weight 1) ──────────────────────────────────────────────────

@pytest.mark.weight(1)
def test_sorted_by_total_spend_desc(query_result_rows):
    """Results must be sorted by total_spend descending."""
    spends = [row["total_spend"] for row in query_result_rows]
    assert spends == sorted(spends, reverse=True), (
        f"Results not sorted desc: {spends}"
    )


@pytest.mark.weight(1)
def test_first_row_is_eva(query_result_rows):
    """First row should be Eva Garcia (highest spend: 870.00)."""
    assert query_result_rows[0]["customer_name"] == "Eva Garcia"


@pytest.mark.weight(1)
def test_last_row_is_carol(query_result_rows):
    """Last row should be Carol Jones (lowest spend: 660.00)."""
    assert query_result_rows[-1]["customer_name"] == "Carol Jones"


@pytest.mark.weight(1)
def test_total_spend_david(query_result_rows):
    """David Lee's total spend should be 825.50."""
    for row in query_result_rows:
        if row.get("customer_name") == "David Lee":
            assert abs(row["total_spend"] - 825.50) < 0.01
            return
    pytest.fail("David Lee not found in results")


@pytest.mark.weight(1)
def test_total_spend_carol(query_result_rows):
    """Carol Jones's total spend should be 660.00."""
    for row in query_result_rows:
        if row.get("customer_name") == "Carol Jones":
            assert abs(row["total_spend"] - 660.00) < 0.01
            return
    pytest.fail("Carol Jones not found in results")


@pytest.mark.weight(1)
def test_frank_not_included(query_result_rows):
    """Frank Miller has no orders and should not appear."""
    names = {row["customer_name"] for row in query_result_rows}
    assert "Frank Miller" not in names, "Frank Miller has no orders"


@pytest.mark.weight(1)
def test_results_json_matches_query(results_json, query_result_rows):
    """results.json should match the query output."""
    assert len(results_json) == len(query_result_rows), (
        "results.json row count doesn't match query output"
    )


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
