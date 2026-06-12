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
    path = workspace / "review.json"
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
    path = workspace / "review.json"
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
    path = workspace / "review.json"
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
