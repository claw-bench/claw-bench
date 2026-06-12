"""Verifier for sec-008: Encryption Validation."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def audit(workspace):
    """Load and return the crypto audit JSON."""
    path = workspace / "crypto_audit.json"
    assert path.exists(), "crypto_audit.json not found in workspace"
    data = json.loads(path.read_text())
    assert isinstance(data, list), "crypto_audit.json must contain a JSON array"
    return data


def _find_component_issues(audit, component):
    """Find all issues for a given component."""
    return [e for e in audit if e.get("component") == component]


def test_audit_file_exists(workspace):
    """crypto_audit.json must exist."""
    assert (workspace / "crypto_audit.json").exists()


def test_minimum_findings(audit):
    """Should detect at least 8 security issues."""
    assert len(audit) >= 8, f"Expected at least 8 findings, got {len(audit)}"


def test_web_server_tls_flagged(audit):
    """web_server TLS 1.0 must be flagged."""
    issues = _find_component_issues(audit, "web_server")
    assert len(issues) >= 1, "web_server issues not detected"
    texts = " ".join(e.get("issue", "") + e.get("current_value", "") for e in issues).lower()
    assert "tls" in texts or "1.0" in texts or "rc4" in texts


def test_password_md5_flagged(audit):
    """password_storage MD5 must be flagged."""
    issues = _find_component_issues(audit, "password_storage")
    assert len(issues) >= 1, "password_storage MD5 not detected"
    texts = " ".join(e.get("issue", "") for e in issues).lower()
    assert "md5" in texts or "broken" in texts or "weak" in texts


def test_file_encryption_des_flagged(audit):
    """file_encryption DES must be flagged."""
    issues = _find_component_issues(audit, "file_encryption")
    assert len(issues) >= 1, "file_encryption DES not detected"


def test_email_cert_validation_flagged(audit):
    """email_service disabled certificate validation must be flagged."""
    issues = _find_component_issues(audit, "email_service")
    assert len(issues) >= 1, "email_service issues not detected"


def test_internal_api_no_encryption_flagged(audit):
    """internal_api with no transport encryption must be flagged."""
    issues = _find_component_issues(audit, "internal_api")
    assert len(issues) >= 1, "internal_api issues not detected"
    texts = " ".join(e.get("issue", "") for e in issues).lower()
    assert "encrypt" in texts or "none" in texts or "1024" in texts or "sha1" in texts or "sha-1" in texts


def test_each_entry_has_required_fields(audit):
    """Each entry must have component, setting, current_value, issue, recommendation, severity."""
    for entry in audit:
        assert "component" in entry, "Missing 'component' field"
        assert "issue" in entry, "Missing 'issue' field"
        assert "recommendation" in entry, "Missing 'recommendation' field"
        assert "severity" in entry, "Missing 'severity' field"


def test_severity_values(audit):
    """Severity must be critical, high, medium, or low."""
    valid = {"critical", "high", "medium", "low"}
    for entry in audit:
        assert entry["severity"] in valid, f"Invalid severity: {entry['severity']}"


def test_database_not_flagged(audit):
    """database component (properly configured) should not be flagged."""
    issues = _find_component_issues(audit, "database")
    assert len(issues) == 0, "database should not be flagged (properly configured)"


def test_backup_not_flagged(audit):
    """backup_system (properly configured) should not be flagged."""
    issues = _find_component_issues(audit, "backup_system")
    assert len(issues) == 0, "backup_system should not be flagged (properly configured)"


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
    path = workspace / "crypto_config.json"
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
    path = workspace / "crypto_config.json"
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
    path = workspace / "crypto_config.json"
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
