"""Verifier for sec-012: Secrets Scanning in Git History."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def report(workspace):
    """Load and return the secrets report JSON."""
    path = workspace / "secrets_report.json"
    assert path.exists(), "secrets_report.json not found in workspace"
    data = json.loads(path.read_text())
    assert isinstance(data, list), "secrets_report.json must contain a JSON array"
    return data


def _find_by_commit(report, commit_id):
    """Find entries for a given commit."""
    return [r for r in report if r.get("commit") == commit_id]


COMMITS_WITH_SECRETS = ["commit_01", "commit_03", "commit_05", "commit_07", "commit_09"]
CLEAN_COMMITS = ["commit_02", "commit_04", "commit_06", "commit_08", "commit_10"]


def test_report_file_exists(workspace):
    """secrets_report.json must exist."""
    assert (workspace / "secrets_report.json").exists()


def test_minimum_secrets_found(report):
    """Must detect at least 6 secrets."""
    assert len(report) >= 6, f"Expected at least 6 secrets, got {len(report)}"


def test_aws_keys_found(report):
    """AWS credentials in commit_01 must be detected."""
    matches = _find_by_commit(report, "commit_01")
    assert len(matches) >= 1, "AWS credentials in commit_01 not detected"
    types = {m.get("secret_type", "").lower() for m in matches}
    assert any("aws" in t or "key" in t for t in types), (
        f"AWS key type not identified, got: {types}"
    )


def test_database_credential_found(report):
    """Database credential in commit_03 must be detected."""
    matches = _find_by_commit(report, "commit_03")
    assert len(matches) >= 1, "Database credential in commit_03 not detected"


def test_stripe_key_found(report):
    """Stripe API key in commit_05 must be detected."""
    matches = _find_by_commit(report, "commit_05")
    assert len(matches) >= 1, "Stripe/GitHub keys in commit_05 not detected"


def test_private_key_found(report):
    """RSA private key in commit_07 must be detected."""
    matches = _find_by_commit(report, "commit_07")
    assert len(matches) >= 1, "Private key in commit_07 not detected"
    types = {m.get("secret_type", "").lower() for m in matches}
    assert any("private" in t or "key" in t or "pem" in t or "rsa" in t for t in types)


def test_jwt_secret_found(report):
    """JWT secret in commit_09 must be detected."""
    matches = _find_by_commit(report, "commit_09")
    assert len(matches) >= 1, "JWT secret in commit_09 not detected"


def test_clean_commits_not_flagged(report):
    """Clean commits should not be flagged."""
    for commit in CLEAN_COMMITS:
        matches = _find_by_commit(report, commit)
        assert len(matches) == 0, f"Clean commit {commit} incorrectly flagged"


def test_each_entry_has_required_fields(report):
    """Each entry must have commit, file, secret_type, remediation."""
    for entry in report:
        assert "commit" in entry, "Missing 'commit' field"
        assert "file" in entry, "Missing 'file' field"
        assert "secret_type" in entry, "Missing 'secret_type' field"
        assert "remediation" in entry, "Missing 'remediation' field"


def test_remediation_not_empty(report):
    """Each entry must have a non-empty remediation recommendation."""
    for entry in report:
        assert len(entry.get("remediation", "")) > 10, (
            f"Remediation too short for {entry.get('commit')}/{entry.get('file')}"
        )
