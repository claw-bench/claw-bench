"""Verifier for web-007: SEO Analysis."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def report(workspace):
    path = workspace / "seo_report.json"
    assert path.exists(), "seo_report.json not found"
    return json.loads(path.read_text())


def test_output_file_exists(workspace):
    assert (workspace / "seo_report.json").exists()


def test_all_pages_analyzed(report):
    assert len(report["pages"]) == 3


def test_has_total_issues(report):
    assert "total_issues" in report
    assert report["total_issues"] >= 8


def test_has_issue_summary(report):
    assert "issue_summary" in report
    assert isinstance(report["issue_summary"], dict)


def test_about_page_missing_meta(report):
    about = [p for p in report["pages"] if p["file"] == "about.html"][0]
    assert about["has_meta_description"] is False
    assert "missing_meta_description" in about["issues"]


def test_about_page_title_too_short(report):
    about = [p for p in report["pages"] if p["file"] == "about.html"][0]
    assert "title_too_short" in about["issues"]


def test_about_page_missing_h1(report):
    about = [p for p in report["pages"] if p["file"] == "about.html"][0]
    assert about["h1_count"] == 0
    assert "missing_h1" in about["issues"]


def test_services_multiple_h1(report):
    services = [p for p in report["pages"] if p["file"] == "services.html"][0]
    assert services["h1_count"] == 2
    assert "multiple_h1" in services["issues"]


def test_index_has_canonical(report):
    index = [p for p in report["pages"] if p["file"] == "index.html"][0]
    assert index["has_canonical"] is True


def test_about_missing_canonical(report):
    about = [p for p in report["pages"] if p["file"] == "about.html"][0]
    assert about["has_canonical"] is False


def test_missing_alt_detected(report):
    summary = report["issue_summary"]
    assert summary.get("missing_alt", 0) >= 3


def test_pages_have_required_fields(report):
    for page in report["pages"]:
        assert "file" in page
        assert "title" in page
        assert "has_meta_description" in page
        assert "h1_count" in page
        assert "issues" in page


def test_heading_skip_detected(report):
    about = [p for p in report["pages"] if p["file"] == "about.html"][0]
    assert "heading_skip" in about["issues"]
