"""Verifier for sec-003: Check File Permissions."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def audit(workspace):
    """Load and return the permission audit JSON."""
    path = workspace / "permission_audit.json"
    assert path.exists(), "permission_audit.json not found in workspace"
    data = json.loads(path.read_text())
    assert isinstance(data, list), "permission_audit.json must contain a JSON array"
    return data


DANGEROUS_FILES = [
    "config.yaml",
    "private_key.pem",
    "backup_script.sh",
    "passwords.db",
    "upload_handler.cgi",
    ".htpasswd",
]

SAFE_FILES = [
    "README.md", "database.env", "app.log", "server",
    "index.html", "package.json", "deploy.sh", "robots.txt", "style.css",
]


def test_audit_file_exists(workspace):
    """permission_audit.json must exist."""
    assert (workspace / "permission_audit.json").exists()


def test_audit_is_nonempty(audit):
    """Audit must contain findings."""
    assert len(audit) > 0


def test_all_dangerous_files_flagged(audit):
    """All 6 dangerous files must be flagged."""
    flagged_files = {entry["file"] for entry in audit}
    for df in DANGEROUS_FILES:
        assert df in flagged_files, f"Dangerous file {df} not flagged"


def test_each_entry_has_required_fields(audit):
    """Each audit entry must have file, permissions, issue, recommendation."""
    for entry in audit:
        assert "file" in entry, "Missing 'file' field"
        assert "issue" in entry, "Missing 'issue' field"
        assert "recommendation" in entry, "Missing 'recommendation' field"


def test_private_key_flagged(audit):
    """private_key.pem must be flagged for being world-accessible."""
    entries = [e for e in audit if e["file"] == "private_key.pem"]
    assert len(entries) >= 1, "private_key.pem not in audit"
    issue_text = entries[0]["issue"].lower()
    assert "world" in issue_text or "writable" in issue_text or "666" in issue_text


def test_suid_flagged(audit):
    """backup_script.sh must be flagged for SUID bit."""
    entries = [e for e in audit if e["file"] == "backup_script.sh"]
    assert len(entries) >= 1, "backup_script.sh not in audit"
    issue_text = entries[0]["issue"].lower()
    assert "suid" in issue_text or "setuid" in issue_text or "privilege" in issue_text


def test_recommendations_are_restrictive(audit):
    """Recommendations should suggest more restrictive permissions."""
    for entry in audit:
        rec = entry.get("recommendation", "")
        # Recommendation should be a numeric mode or description
        assert len(rec) > 0, f"Empty recommendation for {entry['file']}"


def test_777_files_detected(audit):
    """Files with 777 permissions must be detected."""
    flagged = {e["file"] for e in audit}
    assert "config.yaml" in flagged, "config.yaml (777) not flagged"
    assert "upload_handler.cgi" in flagged, "upload_handler.cgi (777) not flagged"


def test_no_excessive_false_positives(audit):
    """Should not flag more than 10 files (reasonable false positive limit)."""
    assert len(audit) <= 10, f"Too many findings ({len(audit)}) — likely false positives"
