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
