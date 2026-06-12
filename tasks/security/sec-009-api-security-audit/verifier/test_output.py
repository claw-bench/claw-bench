"""Verifier for sec-009: API Security Audit."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def audit(workspace):
    """Load and return the API audit JSON."""
    path = workspace / "api_audit.json"
    assert path.exists(), "api_audit.json not found in workspace"
    data = json.loads(path.read_text())
    assert isinstance(data, list), "api_audit.json must contain a JSON array"
    return data


def _find_by_endpoint(audit, endpoint_substring):
    """Find entries matching an endpoint substring."""
    return [e for e in audit if endpoint_substring.lower() in e.get("endpoint", "").lower()]


def _find_by_category(audit, category):
    """Find entries matching a category."""
    return [e for e in audit if e.get("category") == category]


def test_audit_file_exists(workspace):
    """api_audit.json must exist."""
    assert (workspace / "api_audit.json").exists()


def test_minimum_findings(audit):
    """Should detect at least 7 security issues."""
    assert len(audit) >= 7, f"Expected at least 7 findings, got {len(audit)}"


def test_unauthenticated_user_listing(audit):
    """GET /users with no auth must be flagged."""
    matches = _find_by_endpoint(audit, "/users")
    auth_issues = [m for m in matches if "auth" in m.get("category", "").lower()
                   or "auth" in m.get("description", "").lower()]
    assert len(auth_issues) >= 1, "Unauthenticated GET /users not detected"


def test_pii_exposure_detected(audit):
    """PII exposure (SSN, DOB) must be flagged."""
    pii = _find_by_category(audit, "pii_exposure")
    assert len(pii) >= 1, "PII exposure not detected"


def test_unauthenticated_delete(audit):
    """DELETE /users/{id} with no auth must be flagged."""
    matches = _find_by_endpoint(audit, "delete")
    if not matches:
        matches = [e for e in audit if "delete" in e.get("description", "").lower()
                   and "user" in e.get("description", "").lower()]
    assert len(matches) >= 1, "Unauthenticated DELETE endpoint not detected"


def test_cors_misconfiguration(audit):
    """Wildcard CORS origin must be flagged."""
    cors = _find_by_category(audit, "cors")
    assert len(cors) >= 1, "CORS misconfiguration not detected"


def test_login_rate_limiting(audit):
    """Login endpoint missing rate limiting must be flagged."""
    rate = _find_by_category(audit, "rate_limiting")
    assert len(rate) >= 1, "Missing rate limiting on login not detected"


def test_export_endpoint_flagged(audit):
    """Unauthenticated /export/users must be flagged."""
    matches = _find_by_endpoint(audit, "export")
    assert len(matches) >= 1, "Unauthenticated export endpoint not detected"


def test_each_entry_has_required_fields(audit):
    """Each entry must have endpoint, category, description, severity, recommendation."""
    for entry in audit:
        assert "endpoint" in entry, "Missing 'endpoint' field"
        assert "category" in entry, "Missing 'category' field"
        assert "description" in entry, "Missing 'description' field"
        assert "severity" in entry, "Missing 'severity' field"
        assert "recommendation" in entry, "Missing 'recommendation' field"


def test_severity_values(audit):
    """Severity must be valid."""
    valid = {"critical", "high", "medium", "low"}
    for entry in audit:
        assert entry["severity"] in valid, f"Invalid severity: {entry['severity']}"


def test_health_endpoint_not_flagged(audit):
    """Health check endpoint should not be flagged for missing auth."""
    health = _find_by_endpoint(audit, "/health")
    auth_flags = [h for h in health if h.get("category") == "authentication"]
    assert len(auth_flags) == 0, "Health endpoint should not require authentication"


# ── Enhanced checks (auto-generated) ────────────────────────────────────────

@pytest.mark.weight(1)
def test_no_placeholder_values(workspace):
    """Output files must not contain placeholder/TODO markers."""
    placeholders = ["PLACEHOLDER", "CHANGEME"]
    for f in workspace.iterdir():
        if f.is_file() and f.suffix in (".json", ".csv", ".txt", ".md", ".py", ".yaml", ".yml", ".html", ".xml"):
            content = f.read_text(errors="replace")
            for p in placeholders:
                assert p not in content, f"Placeholder '{p}' found in {f.name}"

@pytest.mark.weight(2)
def test_no_empty_critical_fields(workspace):
    """JSON output must not have empty-string or null values in top-level fields."""
    import json
    path = workspace / "api_spec.json"
    if not path.exists():
        pytest.skip("output file not found")
    data = json.loads(path.read_text())
    items = data if isinstance(data, list) else [data]
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        non_empty = [
            v for v in item.values()
            if v is not None and (not isinstance(v, str) or v.strip() != "")
        ]
        assert non_empty, f"Item {i}: all fields are empty or null"

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
    path = workspace / "api_spec.json"
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
    classified = snake + camel + pascal
    if classified == 0:
        return
    consistency = dominant / classified
    assert consistency >= 0.7, f"Key naming inconsistent: {snake} snake, {camel} camel, {pascal} pascal out of {len(all_keys)} keys"

@pytest.mark.weight(1)
def test_no_duplicate_entries(workspace):
    """Output should not contain exact duplicate rows/objects."""
    import json
    path = workspace / "api_spec.json"
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
    bad_patterns = [".DS_Store", "Thumbs.db", ".bak", ".tmp"]
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
