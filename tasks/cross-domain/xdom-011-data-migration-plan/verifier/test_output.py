"""Verifier for xdom-011: Data Migration Plan."""

import ast
import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def mapping(workspace):
    path = workspace / "mapping.json"
    assert path.exists(), "mapping.json not found"
    with open(path) as f:
        return json.load(f)


@pytest.fixture
def migration_script(workspace):
    path = workspace / "migration_script.py"
    assert path.exists(), "migration_script.py not found"
    return path.read_text()


@pytest.fixture
def validation_report(workspace):
    path = workspace / "validation_report.json"
    assert path.exists(), "validation_report.json not found"
    with open(path) as f:
        return json.load(f)


@pytest.fixture
def rollback_plan(workspace):
    path = workspace / "rollback_plan.md"
    assert path.exists(), "rollback_plan.md not found"
    return path.read_text()


def test_mapping_exists(workspace):
    """mapping.json must exist."""
    assert (workspace / "mapping.json").exists()


def test_migration_script_exists(workspace):
    """migration_script.py must exist."""
    assert (workspace / "migration_script.py").exists()


def test_validation_report_exists(workspace):
    """validation_report.json must exist."""
    assert (workspace / "validation_report.json").exists()


def test_rollback_plan_exists(workspace):
    """rollback_plan.md must exist."""
    assert (workspace / "rollback_plan.md").exists()


def test_mapping_covers_source_fields(mapping):
    """Mapping must cover key source fields."""
    source_fields = {m.get("source_field") for m in mapping.get("mappings", [])}
    required_source = {"cust_id", "full_name", "email_addr", "status", "created"}
    missing = required_source - source_fields
    assert not missing, f"Source fields not mapped: {missing}"


def test_mapping_covers_target_fields(mapping):
    """Mapping must reference key target fields."""
    target_fields = {m.get("target_field") for m in mapping.get("mappings", [])}
    required_target = {"first_name", "last_name", "email", "status", "created_at"}
    missing = required_target - target_fields
    assert not missing, f"Target fields not covered: {missing}"


def test_mapping_has_name_split(mapping):
    """Mapping must handle full_name -> first_name + last_name split."""
    mappings = mapping.get("mappings", [])
    name_mappings = [m for m in mappings if m.get("source_field") == "full_name"]
    target_names = {m.get("target_field") for m in name_mappings}
    assert "first_name" in target_names, "full_name must map to first_name"
    assert "last_name" in target_names, "full_name must map to last_name"


def test_mapping_has_address_merge(mapping):
    """Mapping must merge address fields into address JSON."""
    mappings = mapping.get("mappings", [])
    addr_sources = {m.get("source_field") for m in mappings if m.get("target_field") == "address"}
    assert len(addr_sources) >= 2, "Multiple address fields should merge into address"


def test_migration_script_valid_python(migration_script):
    """migration_script.py must be syntactically valid Python."""
    try:
        ast.parse(migration_script)
    except SyntaxError as e:
        pytest.fail(f"migration_script.py has syntax error: {e}")


def test_migration_script_has_functions(migration_script):
    """Script must have read, transform, and validate functions."""
    tree = ast.parse(migration_script)
    func_names = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    assert any("read" in f for f in func_names), "Missing read function"
    assert any("transform" in f or "map" in f for f in func_names), "Missing transform function"
    assert any("valid" in f for f in func_names), "Missing validate function"


def test_migration_script_has_main(migration_script):
    """Script must have a main execution block."""
    assert '__name__' in migration_script and '__main__' in migration_script, \
        "Missing if __name__ == '__main__' block"


def test_validation_report_has_checks(validation_report):
    """Validation report must contain validation checks."""
    checks = validation_report.get("validation_checks", validation_report.get("checks", []))
    assert len(checks) >= 3, f"Expected at least 3 validation checks, got {len(checks)}"


def test_validation_identifies_date_issues(validation_report):
    """Validation should flag date format inconsistencies."""
    content = json.dumps(validation_report).lower()
    assert "date" in content, "Validation should mention date format issues"


def test_rollback_has_backup_steps(rollback_plan):
    """Rollback plan must include backup steps."""
    lower = rollback_plan.lower()
    assert "backup" in lower, "Rollback plan should mention backup"


def test_rollback_has_restore_procedure(rollback_plan):
    """Rollback plan must include restore/rollback procedure."""
    lower = rollback_plan.lower()
    assert "restore" in lower or "rollback" in lower, "Rollback plan should describe restore procedure"


def test_rollback_has_verification(rollback_plan):
    """Rollback plan must include verification steps."""
    lower = rollback_plan.lower()
    assert "verif" in lower or "check" in lower or "confirm" in lower, \
        "Rollback plan should include verification steps"


def test_rollback_has_timeline(rollback_plan):
    """Rollback plan should estimate rollback time."""
    lower = rollback_plan.lower()
    assert "time" in lower or "minute" in lower or "duration" in lower or "estimat" in lower, \
        "Rollback plan should estimate rollback duration"
