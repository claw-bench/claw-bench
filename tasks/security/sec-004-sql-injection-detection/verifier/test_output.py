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
    path = workspace / "vulnerabilities.json"
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
    path = workspace / "vulnerabilities.json"
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
    path = workspace / "vulnerabilities.json"
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
