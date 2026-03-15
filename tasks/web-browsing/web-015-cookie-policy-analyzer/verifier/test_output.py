"""Verifier for web-015: Analyze Cookie Policy for Privacy Compliance."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return request.config.getoption("--workspace")


@pytest.fixture
def report(workspace):
    path = Path(workspace) / "cookie_report.json"
    assert path.exists(), "cookie_report.json not found in workspace"
    return json.loads(path.read_text())


def test_output_file_exists(workspace):
    assert (Path(workspace) / "cookie_report.json").exists()


def test_top_level_keys(report):
    assert "summary" in report
    assert "privacy_score" in report
    assert "issues" in report


def test_total_cookies(report):
    assert report["summary"]["total_cookies"] == 12


def test_by_category(report):
    cats = report["summary"]["by_category"]
    assert cats["essential"] == 3
    assert cats["functional"] == 3
    assert cats["analytics"] == 3
    assert cats["tracking"] == 3


def test_third_party_count(report):
    assert report["summary"]["third_party_count"] == 5


def test_secure_count(report):
    assert report["summary"]["secure_count"] == 8


def test_httponly_count(report):
    assert report["summary"]["httponly_count"] == 3


def test_privacy_score(report):
    # 100 - 4*5(no secure) - 9*5(no httponly) - 5*3(3rd party) - 3*10(tracking) = -10 -> 0
    assert report["privacy_score"] == 0


def test_issues_is_list(report):
    assert isinstance(report["issues"], list)


def test_issues_not_empty(report):
    assert len(report["issues"]) > 0


def test_issue_structure(report):
    for issue in report["issues"]:
        assert "cookie_name" in issue
        assert "issue" in issue


def test_missing_secure_flags(report):
    secure_issues = [i for i in report["issues"] if i["issue"] == "missing_secure_flag"]
    names = {i["cookie_name"] for i in secure_issues}
    assert names == {"theme", "ad_tracker", "ab_test", "retarget"}


def test_missing_httponly_flags(report):
    httponly_issues = [i for i in report["issues"] if i["issue"] == "missing_httponly_flag"]
    names = {i["cookie_name"] for i in httponly_issues}
    expected = {"user_prefs", "theme", "_ga", "_gid", "fb_pixel", "ad_tracker", "lang", "ab_test", "retarget"}
    assert names == expected


def test_third_party_tracking(report):
    tp_issues = [i for i in report["issues"] if i["issue"] == "third_party_tracking"]
    names = {i["cookie_name"] for i in tp_issues}
    assert names == {"_ga", "_gid", "fb_pixel", "ad_tracker", "retarget"}


def test_no_samesite_issues(report):
    samesite_issues = [i for i in report["issues"] if i["issue"] == "no_samesite"]
    names = {i["cookie_name"] for i in samesite_issues}
    assert names == {"_ga", "_gid", "fb_pixel", "ad_tracker", "retarget", "ab_test"}


def test_issues_sorted(report):
    issues = report["issues"]
    for i in range(len(issues) - 1):
        key_a = (issues[i]["cookie_name"], issues[i]["issue"])
        key_b = (issues[i + 1]["cookie_name"], issues[i + 1]["issue"])
        assert key_a <= key_b, f"Issues not sorted: {key_a} > {key_b}"
