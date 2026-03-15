"""Verifier for xdom-002: Code Review Report."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def review(workspace):
    path = workspace / "review.json"
    assert path.exists(), "review.json not found in workspace"
    with open(path) as f:
        return json.load(f)


@pytest.fixture
def review_summary(workspace):
    path = workspace / "review_summary.md"
    assert path.exists(), "review_summary.md not found in workspace"
    return path.read_text()


def test_review_json_exists(workspace):
    """review.json must exist."""
    assert (workspace / "review.json").exists()


def test_review_summary_exists(workspace):
    """review_summary.md must exist."""
    assert (workspace / "review_summary.md").exists()


def test_review_has_required_fields(review):
    """review.json must have file, total_issues, and issues fields."""
    assert "issues" in review, "Missing 'issues' field"
    assert "total_issues" in review or len(review.get("issues", [])) > 0


def test_minimum_issues_found(review):
    """At least 5 issues must be identified."""
    issues = review.get("issues", [])
    assert len(issues) >= 5, f"Expected at least 5 issues, got {len(issues)}"


def test_issue_fields_complete(review):
    """Each issue must have line, severity, category, description, and suggestion."""
    required = {"line", "severity", "category", "description", "suggestion"}
    for i, issue in enumerate(review.get("issues", [])):
        missing = required - set(issue.keys())
        assert not missing, f"Issue {i} missing fields: {missing}"


def test_severity_values_valid(review):
    """Severity must be one of: low, medium, high, critical."""
    valid = {"low", "medium", "high", "critical"}
    for issue in review.get("issues", []):
        assert issue["severity"] in valid, f"Invalid severity: {issue['severity']}"


def test_category_values_valid(review):
    """Category must be one of: style, bug, security, performance."""
    valid = {"style", "bug", "security", "performance"}
    for issue in review.get("issues", []):
        assert issue["category"] in valid, f"Invalid category: {issue['category']}"


def test_sql_injection_detected(review):
    """SQL injection vulnerability must be detected."""
    issues = review.get("issues", [])
    descriptions = " ".join(i.get("description", "").lower() + " " + i.get("category", "").lower() for i in issues)
    assert "sql" in descriptions or "injection" in descriptions or "query" in descriptions, \
        "SQL injection issue not detected"


def test_hardcoded_credentials_detected(review):
    """Hardcoded credentials must be detected."""
    issues = review.get("issues", [])
    descriptions = " ".join(i.get("description", "").lower() for i in issues)
    assert any(w in descriptions for w in ["hardcoded", "credential", "password", "secret"]), \
        "Hardcoded credentials issue not detected"


def test_pickle_issue_detected(review):
    """Unsafe pickle deserialization must be detected."""
    issues = review.get("issues", [])
    descriptions = " ".join(i.get("description", "").lower() for i in issues)
    assert any(w in descriptions for w in ["pickle", "deserialization", "deserializ", "unsafe"]), \
        "Unsafe pickle deserialization not detected"


def test_bug_category_present(review):
    """At least one bug must be identified."""
    categories = [i.get("category") for i in review.get("issues", [])]
    assert "bug" in categories, "No bug category issues found"


def test_style_category_present(review):
    """At least one style issue must be identified."""
    categories = [i.get("category") for i in review.get("issues", [])]
    assert "style" in categories, "No style category issues found"


def test_summary_has_recommendation(review_summary):
    """Summary must include an overall recommendation."""
    lower = review_summary.lower()
    assert any(w in lower for w in ["recommend", "request changes", "approve", "reject"]), \
        "Summary missing recommendation section"


def test_summary_mentions_issues(review_summary):
    """Summary must mention specific issues."""
    lower = review_summary.lower()
    assert "sql" in lower or "injection" in lower, "Summary should mention SQL injection"
    assert "credential" in lower or "password" in lower or "hardcoded" in lower, \
        "Summary should mention hardcoded credentials"
