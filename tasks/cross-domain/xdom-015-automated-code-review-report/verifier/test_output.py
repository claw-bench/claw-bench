"""Verifier for xdom-015: Automated Code Review Report."""

import json
import os
import re

import pytest

WORKSPACE = os.environ.get(
    "WORKSPACE",
    os.path.join(os.path.dirname(__file__), "..", "workspace"),
)


@pytest.fixture
def review():
    path = os.path.join(WORKSPACE, "review.json")
    assert os.path.exists(path), "review.json not found in workspace"
    with open(path) as f:
        data = json.load(f)
    return data


class TestReviewStructure:
    """Verify the review has all required top-level fields."""

    REQUIRED_FIELDS = [
        "files_reviewed",
        "issues",
        "summary",
        "overall_score",
        "recommendation",
    ]

    def test_required_fields_present(self, review):
        for field in self.REQUIRED_FIELDS:
            assert field in review, f"Missing required field: {field}"

    def test_recommendation_valid(self, review):
        valid = {"request_changes", "approve_with_comments", "approve"}
        assert review["recommendation"] in valid, (
            f"recommendation must be one of {valid}"
        )

    def test_overall_score_range(self, review):
        score = review["overall_score"]
        assert isinstance(score, (int, float)), "overall_score must be numeric"
        assert 0 <= score <= 100, f"overall_score must be 0-100, got {score}"


class TestFilesReviewed:
    """Verify files_reviewed correctness."""

    EXPECTED_FILES = [
        "app/auth/handlers.py",
        "app/models/user.py",
        "app/api/routes.py",
        "app/utils/helpers.py",
    ]

    def test_files_reviewed_count(self, review):
        assert len(review["files_reviewed"]) == 4, (
            f"Expected 4 files reviewed, got {len(review['files_reviewed'])}"
        )

    def test_all_diff_files_present(self, review):
        reviewed_files = [f["file"] for f in review["files_reviewed"]]
        for expected in self.EXPECTED_FILES:
            assert any(expected in rf for rf in reviewed_files), (
                f"File {expected} should be in files_reviewed"
            )

    def test_files_have_required_fields(self, review):
        for f in review["files_reviewed"]:
            assert "file" in f, "Each file entry must have 'file' field"


class TestIssues:
    """Verify issues are correctly identified."""

    def test_minimum_issue_count(self, review):
        assert len(review["issues"]) >= 8, (
            f"Expected at least 8 issues, got {len(review['issues'])}"
        )

    def test_issues_have_required_fields(self, review):
        required = {"file", "severity", "category", "description"}
        for i, issue in enumerate(review["issues"]):
            for field in required:
                assert field in issue, (
                    f"Issue {i} missing field '{field}'"
                )

    def test_issue_severities_valid(self, review):
        valid = {"error", "warning", "info"}
        for i, issue in enumerate(review["issues"]):
            assert issue["severity"] in valid, (
                f"Issue {i} has invalid severity '{issue['severity']}'"
            )

    def test_issue_ids_are_sequential(self, review):
        """If issues have IDs, they should be sequential."""
        ids = [iss.get("id", "") for iss in review["issues"]]
        numbered = []
        for iid in ids:
            m = re.match(r'ISS-(\d+)', iid)
            if m:
                numbered.append(int(m.group(1)))
        if numbered:
            for i in range(1, len(numbered)):
                assert numbered[i] == numbered[i - 1] + 1, (
                    f"Issue IDs not sequential: {numbered[i-1]} -> {numbered[i]}"
                )

    def test_issues_reference_diff_files(self, review):
        """All issues should reference files from the diff."""
        diff_files = {"app/auth/handlers.py", "app/models/user.py",
                      "app/api/routes.py", "app/utils/helpers.py"}
        for i, issue in enumerate(review["issues"]):
            assert any(df in issue["file"] for df in diff_files), (
                f"Issue {i} references unknown file '{issue['file']}'"
            )

    def test_issues_have_line_numbers(self, review):
        """Most issues should have line numbers."""
        with_lines = sum(1 for iss in review["issues"] if "line" in iss and iss["line"])
        assert with_lines >= len(review["issues"]) * 0.7, (
            "At least 70% of issues should have line numbers"
        )


class TestSecurityIssuesDetected:
    """Verify critical security issues are found."""

    def _issues_text(self, review):
        return " ".join(
            (iss.get("description", "") + " " + iss.get("rule", "") + " " +
             iss.get("category", "") + " " + iss.get("code_snippet", "")).lower()
            for iss in review["issues"]
        )

    def test_sql_injection_found(self, review):
        text = self._issues_text(review)
        assert any(kw in text for kw in ["sql injection", "sql", "sec-01", "parameterized"]), (
            "Should detect SQL injection vulnerability"
        )

    def test_hardcoded_secret_found(self, review):
        text = self._issues_text(review)
        assert any(kw in text for kw in [
            "hardcoded", "hardcode", "secret", "sec-02", "password"
        ]), "Should detect hardcoded secrets"

    def test_md5_weakness_found(self, review):
        text = self._issues_text(review)
        assert any(kw in text for kw in ["md5", "weak hash", "sec-06", "insecure hash"]), (
            "Should detect MD5 usage for passwords"
        )

    def test_eval_or_pickle_found(self, review):
        text = self._issues_text(review)
        assert any(kw in text for kw in ["eval", "pickle", "sec-03", "deserialization"]), (
            "Should detect eval() or pickle.loads() usage"
        )

    def test_path_traversal_found(self, review):
        text = self._issues_text(review)
        assert any(kw in text for kw in [
            "path traversal", "path", "sec-05", "filename", "directory traversal"
        ]), "Should detect path traversal vulnerability"


class TestSummaryConsistency:
    """Verify summary statistics are consistent."""

    def test_total_issues_matches(self, review):
        summary = review.get("summary", {})
        assert summary.get("total_issues") == len(review["issues"]), (
            f"summary.total_issues ({summary.get('total_issues')}) != "
            f"len(issues) ({len(review['issues'])})"
        )

    def test_by_severity_sums_to_total(self, review):
        summary = review.get("summary", {})
        by_sev = summary.get("by_severity", {})
        total = sum(by_sev.values())
        assert total == len(review["issues"]), (
            f"by_severity sum ({total}) != total issues ({len(review['issues'])})"
        )

    def test_by_category_sums_to_total(self, review):
        summary = review.get("summary", {})
        by_cat = summary.get("by_category", {})
        total = sum(by_cat.values())
        assert total == len(review["issues"]), (
            f"by_category sum ({total}) != total issues ({len(review['issues'])})"
        )

    def test_total_files_matches(self, review):
        summary = review.get("summary", {})
        if "total_files" in summary:
            assert summary["total_files"] == len(review["files_reviewed"]), (
                "summary.total_files should match files_reviewed length"
            )


class TestScoreAndRecommendation:
    """Verify scoring logic."""

    def test_score_reflects_issues(self, review):
        """Score should be less than 100 given the number of issues."""
        assert review["overall_score"] < 100, (
            "Score should be < 100 given the issues in the diff"
        )

    def test_recommendation_matches_severity(self, review):
        """If there are error-severity issues, recommendation should be request_changes."""
        has_errors = any(
            iss["severity"] == "error" for iss in review["issues"]
        )
        if has_errors:
            assert review["recommendation"] == "request_changes", (
                "With error-severity issues, recommendation should be 'request_changes'"
            )

    def test_score_not_too_high(self, review):
        """Given the many issues in the diff, score should be reasonably low."""
        assert review["overall_score"] <= 70, (
            f"Score {review['overall_score']} seems too high for a diff with this many security issues"
        )
