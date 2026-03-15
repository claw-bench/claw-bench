"""Verifier for web-006: Accessibility Audit."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def report(workspace):
    path = workspace / "accessibility_report.json"
    assert path.exists(), "accessibility_report.json not found"
    return json.loads(path.read_text())


def test_output_file_exists(workspace):
    assert (workspace / "accessibility_report.json").exists()


def test_files_scanned(report):
    assert report["files_scanned"] == 3


def test_has_issues(report):
    assert report["total_issues"] >= 10


def test_missing_alt_found(report):
    alt_issues = [i for i in report["issues"] if i["category"] == "missing_alt"]
    assert len(alt_issues) >= 4, "Should find at least 4 missing alt attributes"


def test_missing_label_found(report):
    label_issues = [i for i in report["issues"] if i["category"] == "missing_label"]
    assert len(label_issues) >= 2, "Should find at least 2 missing labels"


def test_missing_lang_found(report):
    lang_issues = [i for i in report["issues"] if i["category"] == "missing_lang"]
    assert len(lang_issues) >= 1, "index.html is missing lang attribute"


def test_skipped_heading_found(report):
    heading_issues = [i for i in report["issues"] if i["category"] == "skipped_heading"]
    assert len(heading_issues) >= 1, "Should detect skipped heading levels"


def test_empty_link_found(report):
    link_issues = [i for i in report["issues"] if i["category"] == "empty_link"]
    assert len(link_issues) >= 1, "about.html has empty link"


def test_missing_table_header_found(report):
    table_issues = [i for i in report["issues"] if i["category"] == "missing_table_header"]
    assert len(table_issues) >= 1, "products.html table has no th elements"


def test_all_files_have_issues(report):
    files_with_issues = set(i["file"] for i in report["issues"])
    assert len(files_with_issues) == 3, "All 3 files should have issues"


def test_summary_matches_issues(report):
    from collections import Counter
    expected = Counter(i["category"] for i in report["issues"])
    for cat, count in expected.items():
        assert report["summary"].get(cat) == count, f"Summary mismatch for {cat}"


def test_issues_have_required_fields(report):
    for issue in report["issues"]:
        assert "file" in issue
        assert "category" in issue
        assert "description" in issue


def test_clickable_div_detected(report):
    div_issues = [i for i in report["issues"] if i["category"] == "clickable_div"]
    assert len(div_issues) >= 1, "Should detect clickable div without role"
