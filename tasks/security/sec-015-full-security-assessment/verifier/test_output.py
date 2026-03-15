"""Verifier for sec-015: Full Security Assessment."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def assessment(workspace):
    """Load and return the assessment JSON."""
    path = workspace / "assessment.json"
    assert path.exists(), "assessment.json not found in workspace"
    data = json.loads(path.read_text())
    return data


@pytest.fixture
def remediation_plan(workspace):
    """Load and return the remediation plan markdown."""
    path = workspace / "remediation_plan.md"
    assert path.exists(), "remediation_plan.md not found in workspace"
    return path.read_text()


def test_assessment_file_exists(workspace):
    """assessment.json must exist."""
    assert (workspace / "assessment.json").exists()


def test_remediation_plan_exists(workspace):
    """remediation_plan.md must exist."""
    assert (workspace / "remediation_plan.md").exists()


def test_has_executive_summary(assessment):
    """Assessment must include an executive summary."""
    assert "executive_summary" in assessment


def test_has_findings(assessment):
    """Assessment must include findings array."""
    assert "findings" in assessment
    assert isinstance(assessment["findings"], list)


def test_minimum_findings_count(assessment):
    """Must identify at least 10 findings."""
    assert len(assessment["findings"]) >= 10, (
        f"Expected at least 10 findings, got {len(assessment['findings'])}"
    )


def test_findings_span_multiple_categories(assessment):
    """Findings must cover at least 3 different categories."""
    categories = {f.get("category") for f in assessment["findings"]}
    assert len(categories) >= 3, (
        f"Only {len(categories)} categories, expected at least 3: {categories}"
    )


def test_sql_injection_found(assessment):
    """SQL injection vulnerability must be detected."""
    findings_text = " ".join(
        f.get("title", "") + " " + f.get("description", "")
        for f in assessment["findings"]
    ).lower()
    assert "sql injection" in findings_text or "sql" in findings_text


def test_pickle_deserialization_found(assessment):
    """Insecure deserialization via pickle must be detected."""
    findings_text = " ".join(
        f.get("title", "") + " " + f.get("description", "")
        for f in assessment["findings"]
    ).lower()
    assert "pickle" in findings_text or "deserialization" in findings_text


def test_hardcoded_secret_found(assessment):
    """Hardcoded secret key must be detected."""
    findings_text = " ".join(
        f.get("title", "") + " " + f.get("description", "")
        for f in assessment["findings"]
    ).lower()
    assert "secret" in findings_text or "hardcoded" in findings_text or "hardcode" in findings_text


def test_md5_weakness_found(assessment):
    """MD5 password hashing must be flagged."""
    findings_text = " ".join(
        f.get("title", "") + " " + f.get("description", "")
        for f in assessment["findings"]
    ).lower()
    assert "md5" in findings_text or "password hash" in findings_text or "weak hash" in findings_text


def test_container_issues_found(assessment):
    """Docker/container security issues must be detected."""
    findings_text = " ".join(
        f.get("title", "") + " " + f.get("description", "")
        for f in assessment["findings"]
    ).lower()
    assert "root" in findings_text or "container" in findings_text or "docker" in findings_text or "privileged" in findings_text


def test_each_finding_has_required_fields(assessment):
    """Each finding must have id, category, severity, title, description, remediation."""
    for f in assessment["findings"]:
        assert "id" in f, "Missing 'id' field"
        assert "category" in f, "Missing 'category' field"
        assert "severity" in f, "Missing 'severity' field"
        assert "title" in f, "Missing 'title' field"
        assert "description" in f, "Missing 'description' field"
        assert "remediation" in f, "Missing 'remediation' field"


def test_severity_values(assessment):
    """Severity must be valid."""
    valid = {"critical", "high", "medium", "low"}
    for f in assessment["findings"]:
        assert f["severity"] in valid, f"Invalid severity: {f['severity']}"


def test_has_critical_findings(assessment):
    """At least one finding must be critical severity."""
    critical = [f for f in assessment["findings"] if f["severity"] == "critical"]
    assert len(critical) >= 1, "Expected at least one critical finding"


def test_remediation_plan_has_priorities(remediation_plan):
    """Remediation plan must include prioritized sections."""
    lower = remediation_plan.lower()
    assert "priority" in lower or "critical" in lower or "immediate" in lower


def test_remediation_plan_mentions_quick_wins(remediation_plan):
    """Remediation plan should mention quick wins or low-effort fixes."""
    lower = remediation_plan.lower()
    assert "quick win" in lower or "low effort" in lower or "immediate" in lower or "easy" in lower


def test_has_risk_summary(assessment):
    """Assessment must include a risk summary."""
    assert "risk_summary" in assessment or "executive_summary" in assessment
