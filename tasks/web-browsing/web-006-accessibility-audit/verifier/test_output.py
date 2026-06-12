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
    path = workspace / "accessibility_report.json"
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
    path = workspace / "accessibility_report.json"
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
    path = workspace / "accessibility_report.json"
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
