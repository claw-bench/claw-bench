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
