"""Verifier for sec-001: Detect Hardcoded Credentials."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def findings(workspace):
    """Load and return the findings JSON."""
    path = workspace / "findings.json"
    assert path.exists(), "findings.json not found in workspace"
    data = json.loads(path.read_text())
    assert isinstance(data, list), "findings.json must contain a JSON array"
    return data


EXPECTED_FINDINGS = [
    {"file": "config.py", "line": 10, "type": "password"},
    {"file": "api_client.py", "line": 14, "type": "api_key"},
    {"file": "api_client.py", "line": 39, "type": "token"},
    {"file": "auth_service.py", "line": 16, "type": "password"},
    {"file": "auth_service.py", "line": 55, "type": "api_key"},
]


def test_findings_file_exists(workspace):
    """findings.json must exist in the workspace."""
    assert (workspace / "findings.json").exists()


def test_findings_is_valid_json_array(findings):
    """findings.json must be a non-empty JSON array."""
    assert len(findings) > 0, "findings.json must not be empty"


def test_all_five_findings_present(findings):
    """All 5 credential leaks must be detected."""
    assert len(findings) >= 5, f"Expected at least 5 findings, got {len(findings)}"


def test_correct_types_identified(findings):
    """Finding types must be one of password, api_key, token."""
    valid_types = {"password", "api_key", "token"}
    for f in findings:
        assert f.get("type") in valid_types, (
            f"Invalid type '{f.get('type')}' — expected one of {valid_types}"
        )
