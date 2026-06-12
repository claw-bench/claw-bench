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
    path = workspace / "assessment.json"
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
    path = workspace / "assessment.json"
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
    path = workspace / "assessment.json"
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
