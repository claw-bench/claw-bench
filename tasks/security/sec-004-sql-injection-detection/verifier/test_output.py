"""Verifier for sec-004: SQL Injection Detection."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def vulns(workspace):
    """Load and return the vulnerabilities JSON."""
    path = workspace / "vulnerabilities.json"
    assert path.exists(), "vulnerabilities.json not found in workspace"
    data = json.loads(path.read_text())
    assert isinstance(data, list), "vulnerabilities.json must contain a JSON array"
    return data


VULNERABLE_FUNCTIONS = [
    "search_users_by_name",
    "delete_user_by_email",
    "search_products",
    "get_login_history",
]

SAFE_FUNCTIONS = [
    "get_user_by_id",
    "create_user",
    "get_orders_for_user",
    "update_user_status",
]


def test_vulnerabilities_file_exists(workspace):
    """vulnerabilities.json must exist."""
    assert (workspace / "vulnerabilities.json").exists()


def test_correct_number_of_findings(vulns):
    """Should find exactly 4 vulnerable functions."""
    assert len(vulns) == 4, f"Expected 4 vulnerabilities, got {len(vulns)}"


def test_all_vulnerable_functions_found(vulns):
    """All 4 vulnerable functions must be identified."""
    found = {v["function"] for v in vulns}
    for func in VULNERABLE_FUNCTIONS:
        assert func in found, f"Vulnerable function {func} not detected"


def test_safe_functions_not_flagged(vulns):
    """Safe functions must NOT be flagged."""
    found = {v["function"] for v in vulns}
    for func in SAFE_FUNCTIONS:
        assert func not in found, f"Safe function {func} incorrectly flagged"


def test_each_finding_has_required_fields(vulns):
    """Each finding must have function, line, pattern, description, fix."""
    for v in vulns:
        assert "function" in v, "Missing 'function' field"
        assert "line" in v, "Missing 'line' field"
        assert "pattern" in v, "Missing 'pattern' field"
        assert "fix" in v, "Missing 'fix' field"


def test_fix_suggestions_use_parameterized_queries(vulns):
    """Fix suggestions should reference parameterized queries (using ?)."""
    for v in vulns:
        fix = v.get("fix", "")
        assert "?" in fix or "param" in fix.lower() or "bind" in fix.lower(), (
            f"Fix for {v['function']} should suggest parameterized queries"
        )


def test_line_numbers_are_reasonable(vulns):
    """Line numbers should be positive integers within the file range."""
    for v in vulns:
        assert isinstance(v["line"], int), f"Line must be integer for {v['function']}"
        assert 1 <= v["line"] <= 80, (
            f"Line {v['line']} for {v['function']} is out of expected range"
        )


def test_pattern_types_valid(vulns):
    """Pattern types should describe the injection method."""
    for v in vulns:
        pattern = v.get("pattern", "").lower()
        valid_patterns = [
            "f_string", "fstring", "f-string",
            "string_concatenation", "concatenation",
            "format_string", "format", "percent", "string_format",
            "string formatting",
        ]
        assert any(vp in pattern for vp in valid_patterns), (
            f"Unexpected pattern type '{pattern}' for {v['function']}"
        )
