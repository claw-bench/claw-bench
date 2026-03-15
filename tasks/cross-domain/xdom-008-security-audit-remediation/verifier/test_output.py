"""Verifier for xdom-008: Security Audit with Remediation Patch."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def audit(workspace):
    path = workspace / "audit.json"
    assert path.exists(), "audit.json not found"
    with open(path) as f:
        return json.load(f)


@pytest.fixture
def patch_content(workspace):
    path = workspace / "fix.patch"
    assert path.exists(), "fix.patch not found"
    return path.read_text()


def test_audit_exists(workspace):
    """audit.json must exist."""
    assert (workspace / "audit.json").exists()


def test_patch_exists(workspace):
    """fix.patch must exist."""
    assert (workspace / "fix.patch").exists()


def test_audit_has_vulnerabilities(audit):
    """Audit must contain vulnerabilities list."""
    vulns = audit.get("vulnerabilities", [])
    assert len(vulns) >= 4, f"Expected at least 4 vulnerabilities, got {len(vulns)}"


def test_vulnerability_required_fields(audit):
    """Each vulnerability must have required fields."""
    required = {"file", "severity", "title", "description"}
    for i, vuln in enumerate(audit.get("vulnerabilities", [])):
        missing = required - set(vuln.keys())
        assert not missing, f"Vulnerability {i} missing: {missing}"


def test_severity_values_valid(audit):
    """Severity must be valid."""
    valid = {"low", "medium", "high", "critical"}
    for vuln in audit.get("vulnerabilities", []):
        assert vuln["severity"] in valid


def test_md5_vulnerability_detected(audit):
    """MD5 password hashing must be flagged."""
    vulns = audit.get("vulnerabilities", [])
    descriptions = " ".join(v.get("title", "").lower() + " " + v.get("description", "").lower() for v in vulns)
    assert "md5" in descriptions or "weak hash" in descriptions or "password hash" in descriptions, \
        "MD5 password hashing vulnerability not detected"


def test_eval_vulnerability_detected(audit):
    """eval() code injection must be flagged."""
    vulns = audit.get("vulnerabilities", [])
    descriptions = " ".join(v.get("title", "").lower() + " " + v.get("description", "").lower() for v in vulns)
    assert "eval" in descriptions or "code injection" in descriptions, \
        "eval() vulnerability not detected"


def test_command_injection_detected(audit):
    """Command injection (shell=True or os.popen) must be flagged."""
    vulns = audit.get("vulnerabilities", [])
    descriptions = " ".join(v.get("title", "").lower() + " " + v.get("description", "").lower() for v in vulns)
    assert "command injection" in descriptions or "shell" in descriptions or "os.popen" in descriptions or "subprocess" in descriptions, \
        "Command injection vulnerability not detected"


def test_yaml_vulnerability_detected(audit):
    """Unsafe YAML loading must be flagged."""
    vulns = audit.get("vulnerabilities", [])
    descriptions = " ".join(v.get("title", "").lower() + " " + v.get("description", "").lower() for v in vulns)
    assert "yaml" in descriptions or "deserialization" in descriptions, \
        "Unsafe YAML deserialization not detected"


def test_patch_is_unified_diff(patch_content):
    """Patch must be in unified diff format."""
    assert "---" in patch_content and "+++" in patch_content, \
        "Patch is not in unified diff format"
    assert "@@" in patch_content, "Patch missing hunk headers (@@)"


def test_patch_references_source_files(patch_content):
    """Patch must reference the audited source files."""
    assert "auth.py" in patch_content, "Patch should fix auth.py"
    assert "api.py" in patch_content, "Patch should fix api.py"


def test_patch_fixes_md5(patch_content):
    """Patch should replace MD5 with a secure hashing method."""
    lower = patch_content.lower()
    assert "-" in patch_content  # has removals
    # Should remove md5 usage and add something better
    has_removal = "md5" in lower
    has_replacement = "pbkdf2" in lower or "bcrypt" in lower or "sha256" in lower or "argon" in lower
    assert has_removal and has_replacement, \
        "Patch should replace MD5 with a secure hash"


def test_patch_fixes_eval(patch_content):
    """Patch should remove eval() usage."""
    assert "eval(" in patch_content, "Patch should address eval() usage"


def test_files_audited_count(audit):
    """Should audit 3 files."""
    assert audit.get("files_audited", 0) == 3
