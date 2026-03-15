"""Verifier for sec-010: Network Policy Analysis."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def analysis(workspace):
    """Load and return the policy analysis JSON."""
    path = workspace / "policy_analysis.json"
    assert path.exists(), "policy_analysis.json not found in workspace"
    data = json.loads(path.read_text())
    return data


def test_analysis_file_exists(workspace):
    """policy_analysis.json must exist."""
    assert (workspace / "policy_analysis.json").exists()


def test_has_issues_section(analysis):
    """Analysis must have an issues section."""
    assert "issues" in analysis, "Missing 'issues' section"
    assert isinstance(analysis["issues"], list)


def test_minimum_issues_found(analysis):
    """Must detect at least 5 issues."""
    assert len(analysis["issues"]) >= 5, (
        f"Expected at least 5 issues, got {len(analysis['issues'])}"
    )


def test_overly_permissive_detected(analysis):
    """Rule 7 (allow all) must be flagged as overly permissive."""
    types = [i["type"] for i in analysis["issues"]]
    assert "overly_permissive" in types, "No overly_permissive issues detected"
    ovp = [i for i in analysis["issues"] if i["type"] == "overly_permissive"]
    rule_ids_found = set()
    for issue in ovp:
        for rid in issue.get("rule_ids", []):
            rule_ids_found.add(rid)
    assert 7 in rule_ids_found, "Rule 7 (allow all) not flagged"


def test_redundant_detected(analysis):
    """Duplicate rules (1 and 14) must be flagged as redundant."""
    redundant = [i for i in analysis["issues"] if i["type"] == "redundant"]
    assert len(redundant) >= 1, "No redundant rules detected"


def test_conflict_detected(analysis):
    """Conflicting rules (17 and 18 for RDP) must be detected."""
    conflicts = [i for i in analysis["issues"] if i["type"] == "conflict"]
    assert len(conflicts) >= 1, "No conflicting rules detected"


def test_has_optimized_rules(analysis):
    """Analysis must include an optimized ruleset."""
    assert "optimized_rules" in analysis, "Missing 'optimized_rules' section"
    assert isinstance(analysis["optimized_rules"], list)


def test_optimized_rules_fewer(analysis):
    """Optimized ruleset must have fewer rules than original 20."""
    opt_count = len(analysis["optimized_rules"])
    assert opt_count < 20, f"Optimized rules ({opt_count}) should be fewer than 20"


def test_has_summary(analysis):
    """Analysis must include a summary."""
    assert "summary" in analysis, "Missing 'summary' section"
    summary = analysis["summary"]
    assert "total_rules" in summary
    assert "issues_found" in summary


def test_each_issue_has_required_fields(analysis):
    """Each issue must have rule_ids, type, description, severity."""
    for issue in analysis["issues"]:
        assert "rule_ids" in issue, "Missing 'rule_ids' field"
        assert "type" in issue, "Missing 'type' field"
        assert "description" in issue, "Missing 'description' field"
        assert "severity" in issue, "Missing 'severity' field"


def test_optimized_has_default_deny(analysis):
    """Optimized ruleset must include a default deny rule."""
    rules = analysis["optimized_rules"]
    deny_all = [r for r in rules if r.get("action") == "deny"
                and r.get("source") == "0.0.0.0/0"
                and r.get("destination") == "0.0.0.0/0"]
    assert len(deny_all) >= 1, "Optimized ruleset missing default deny rule"
