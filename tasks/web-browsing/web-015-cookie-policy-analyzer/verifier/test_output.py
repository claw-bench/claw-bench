"""Verifier for web-015: Analyze Cookie Policy for Privacy Compliance."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


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


# ── Enhanced checks (auto-generated) ────────────────────────────────────────

@pytest.mark.weight(1)
def test_no_placeholder_values(workspace):
    """Output files must not contain placeholder/TODO markers."""
    placeholders = ["PLACEHOLDER", "CHANGEME"]
    for f in workspace.iterdir():
        if f.is_file() and f.suffix in (".json", ".csv", ".txt", ".md", ".py", ".yaml", ".yml", ".html", ".xml"):
            content = f.read_text(errors="replace")
            for p in placeholders:
                assert p not in content, f"Placeholder '{p}' found in {f.name}"

@pytest.mark.weight(2)
def test_no_empty_critical_fields(workspace):
    """JSON output must not have empty-string or null values in top-level fields."""
    import json
    path = workspace / "cookies.json"
    if not path.exists():
        pytest.skip("output file not found")
    data = json.loads(path.read_text())
    items = data if isinstance(data, list) else [data]
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        non_empty = [
            v for v in item.values()
            if v is not None and (not isinstance(v, str) or v.strip() != "")
        ]
        assert non_empty, f"Item {i}: all fields are empty or null"

@pytest.mark.weight(1)
def test_encoding_valid(workspace):
    """All text output files must be valid UTF-8."""
    for f in workspace.iterdir():
        if f.is_file() and f.suffix in (".json", ".csv", ".txt", ".md", ".py", ".yaml", ".yml", ".html"):
            try:
                f.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                pytest.fail(f"{f.name} contains invalid UTF-8 encoding")

@pytest.mark.weight(1)
def test_consistent_key_naming(workspace):
    """JSON keys should use a consistent naming convention."""
    import json, re
    path = workspace / "cookies.json"
    if not path.exists():
        pytest.skip("output file not found")
    data = json.loads(path.read_text())
    items = data if isinstance(data, list) else [data]
    all_keys = set()
    for item in items:
        if isinstance(item, dict):
            all_keys.update(item.keys())
    if len(all_keys) < 2:
        return
    snake = sum(1 for k in all_keys if re.match(r'^[a-z][a-z0-9_]*$', k))
    camel = sum(1 for k in all_keys if re.match(r'^[a-z][a-zA-Z0-9]*$', k) and not re.match(r'^[a-z][a-z0-9_]*$', k))
    pascal = sum(1 for k in all_keys if re.match(r'^[A-Z][a-zA-Z0-9]*$', k))
    dominant = max(snake, camel, pascal)
    classified = snake + camel + pascal
    if classified == 0:
        return
    consistency = dominant / classified
    assert consistency >= 0.7, f"Key naming inconsistent: {snake} snake, {camel} camel, {pascal} pascal out of {len(all_keys)} keys"

@pytest.mark.weight(1)
def test_no_duplicate_entries(workspace):
    """Output should not contain exact duplicate rows/objects."""
    import json
    path = workspace / "cookies.json"
    if not path.exists():
        pytest.skip("output file not found")
    text = path.read_text().strip()
    if path.suffix == ".json":
        data = json.loads(text)
        if isinstance(data, list):
            serialized = [json.dumps(item, sort_keys=True) for item in data]
            dupes = len(serialized) - len(set(serialized))
            assert dupes == 0, f"Found {dupes} duplicate entries in {path.name}"
    elif path.suffix == ".csv":
        lines_list = text.splitlines()
        if len(lines_list) > 1:
            data_lines = lines_list[1:]
            dupes = len(data_lines) - len(set(data_lines))
            assert dupes == 0, f"Found {dupes} duplicate rows in {path.name}"

@pytest.mark.weight(1)
def test_no_extraneous_files(workspace):
    """Workspace should not contain debug/temp files."""
    bad_patterns = [".DS_Store", "Thumbs.db", ".bak", ".tmp"]
    for f in workspace.rglob("*"):
        if f.is_file():
            for pat in bad_patterns:
                assert pat not in f.name, f"Extraneous file found: {f.name}"

@pytest.mark.weight(1)
def test_output_not_excessively_large(workspace):
    """Output files should be reasonably sized (< 5MB each)."""
    for f in workspace.iterdir():
        if f.is_file() and f.suffix in (".json", ".csv", ".txt", ".md", ".py", ".yaml", ".yml", ".html"):
            size_mb = f.stat().st_size / (1024 * 1024)
            assert size_mb < 5, f"{f.name} is {size_mb:.1f}MB, exceeds 5MB limit"
