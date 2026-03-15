"""Verifier for sec-014: Compliance Audit."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def report(workspace):
    """Load and return the compliance report JSON."""
    path = workspace / "compliance_report.json"
    assert path.exists(), "compliance_report.json not found in workspace"
    data = json.loads(path.read_text())
    return data


# Expected results for key rules
EXPECTED_PASS = [
    "SEC-001", "SEC-002", "SEC-004", "AUTH-002",
    "DATA-001", "DATA-002", "DATA-004",
    "LOG-001", "LOG-002", "LOG-004", "NET-001",
]

EXPECTED_FAIL = [
    "SEC-003",   # HSTS max_age too low
    "AUTH-001",  # min password length 8 < 12
    "AUTH-003",  # session timeout 60 > 30
    "AUTH-004",  # lockout attempts 10 > 5
    "AUTH-005",  # require_special is false
    "DATA-003",  # backup not encrypted
    "LOG-003",   # log integrity disabled
    "NET-002",   # default policy is allow
    "NET-003",   # SSH password auth enabled
]


def _find_result(report, rule_id):
    """Find a result by rule_id."""
    for r in report.get("results", []):
        if r.get("rule_id") == rule_id:
            return r
    return None


def test_report_file_exists(workspace):
    """compliance_report.json must exist."""
    assert (workspace / "compliance_report.json").exists()


def test_all_20_rules_checked(report):
    """All 20 rules must be checked."""
    results = report.get("results", [])
    assert len(results) == 20, f"Expected 20 results, got {len(results)}"


def test_total_rules_count(report):
    """Report total_rules must be 20."""
    assert report.get("total_rules") == 20


def test_passed_and_failed_sum(report):
    """passed + failed must equal total_rules."""
    assert report.get("passed", 0) + report.get("failed", 0) == 20


def test_known_pass_rules(report):
    """Rules that should pass must be marked pass."""
    for rule_id in EXPECTED_PASS:
        result = _find_result(report, rule_id)
        assert result is not None, f"Rule {rule_id} not found in results"
        assert result["status"] == "pass", (
            f"Rule {rule_id} should pass but got {result['status']}"
        )


def test_known_fail_rules(report):
    """Rules that should fail must be marked fail."""
    for rule_id in EXPECTED_FAIL:
        result = _find_result(report, rule_id)
        assert result is not None, f"Rule {rule_id} not found in results"
        assert result["status"] == "fail", (
            f"Rule {rule_id} should fail but got {result['status']}"
        )


def test_each_result_has_required_fields(report):
    """Each result must have rule_id, status, evidence, config_file."""
    for r in report.get("results", []):
        assert "rule_id" in r, "Missing 'rule_id'"
        assert "status" in r, "Missing 'status'"
        assert "evidence" in r, "Missing 'evidence'"
        assert "config_file" in r, "Missing 'config_file'"


def test_evidence_is_specific(report):
    """Evidence must reference specific values (not just pass/fail)."""
    for r in report.get("results", []):
        evidence = r.get("evidence", "")
        assert len(evidence) > 15, (
            f"Evidence too vague for {r['rule_id']}: '{evidence}'"
        )


def test_password_length_evidence(report):
    """AUTH-001 failure evidence must mention the actual value (8) and required value (12)."""
    result = _find_result(report, "AUTH-001")
    assert result is not None
    evidence = result.get("evidence", "")
    assert "8" in evidence and "12" in evidence, (
        f"AUTH-001 evidence should reference values 8 and 12: '{evidence}'"
    )


def test_backup_encryption_evidence(report):
    """DATA-003 failure evidence must mention backups are not encrypted."""
    result = _find_result(report, "DATA-003")
    assert result is not None
    evidence = result.get("evidence", "").lower()
    assert "false" in evidence or "not encrypted" in evidence or "encrypt" in evidence
