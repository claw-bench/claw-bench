import json
import os
import sqlite3
from pathlib import Path
import pytest

@pytest.fixture
def workspace(request):
    """Resolve workspace from --workspace CLI option."""
    ws = request.config.getoption("--workspace")
    if ws:
        return Path(ws)
    return Path(os.environ.get("CLAW_WORKSPACE", os.environ.get("WORKSPACE", "workspace")))
@pytest.mark.weight(3)
def test_migration_report_exists(workspace):
    report_path = workspace / "migration_report.json"
    assert report_path.exists(), "migration_report.json file does not exist"

@pytest.mark.weight(5)
def test_applied_operations_and_verification(workspace):
    report_path = workspace / "migration_report.json"
    with open(report_path) as f:
        report = json.load(f)

    applied = report.get("applied_operations")
    verification = report.get("verification_results")

    assert isinstance(applied, list), "applied_operations should be a list"
    assert isinstance(verification, list), "verification_results should be a list"
    assert len(applied) == len(verification), "Mismatch in operations and verification results count"

    # All verification results should be boolean
    assert all(isinstance(v, bool) for v in verification), "All verification results must be boolean"

@pytest.mark.weight(7)
def test_schema_changes(workspace):
    db_path = workspace / "app.db"
    report_path = workspace / "migration_report.json"

    with open(report_path) as f:
        report = json.load(f)

    applied = report.get("applied_operations")
    verification = report.get("verification_results")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Helper to get table info
    def get_table_info(table):
        cursor.execute(f"PRAGMA table_info({table})")
        return cursor.fetchall()  # list of tuples

    # Helper to get indexes
    def get_indexes(table):
        cursor.execute(f"PRAGMA index_list({table})")
        return cursor.fetchall()  # list of tuples

    for op, verified in zip(applied, verification):
        op_type = op.get("operation")
        if not verified:
            continue  # skip failed

        if op_type == "add_table":
            table_name = op["table_name"]
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            assert cursor.fetchone() is not None, f"Table {table_name} should exist"

            # Check columns
            columns = op["columns"]
            info = get_table_info(table_name)
            col_names = [col[1] for col in info]
            for col in columns:
                assert col["name"] in col_names, f"Column {col['name']} should exist in {table_name}"

        elif op_type == "add_column":
            table_name = op["table_name"]
            col = op["column"]
            info = get_table_info(table_name)
            col_names = [c[1] for c in info]
            assert col["name"] in col_names, f"Column {col['name']} should exist in {table_name}"

        elif op_type == "add_index":
            table_name = op["table_name"]
            index_name = op["index_name"]
            indexes = get_indexes(table_name)
            index_names = [idx[1] for idx in indexes]
            assert index_name in index_names, f"Index {index_name} should exist on {table_name}"

        elif op_type == "rename_column":
            table_name = op["table_name"]
            old_name = op["old_name"]
            new_name = op["new_name"]
            info = get_table_info(table_name)
            col_names = [c[1] for c in info]
            assert new_name in col_names, f"Renamed column {new_name} should exist in {table_name}"
            assert old_name not in col_names, f"Old column {old_name} should not exist in {table_name}"

    conn.close()
