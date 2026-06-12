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


# ── Enhanced checks (auto-generated) ────────────────────────────────────────

@pytest.mark.weight(1)
def test_no_placeholder_values(workspace):
    """Output files must not contain placeholder/TODO markers."""
    placeholders = ["PLACEHOLDER", "CHANGEME", "your_"]
    for f in workspace.iterdir():
        if f.is_file() and f.suffix in (".json", ".csv", ".txt", ".md", ".py", ".yaml", ".yml", ".html", ".xml"):
            content = f.read_text(errors="replace")
            for p in placeholders:
                assert p not in content, f"Placeholder '{p}' found in {f.name}"

@pytest.mark.weight(2)
def test_no_empty_critical_fields(workspace):
    """JSON output must not have empty-string or null values in top-level fields."""
    import json
    path = workspace / "firewall_rules.json"
    if not path.exists():
        pytest.skip("output file not found")
    data = json.loads(path.read_text())
    items = data if isinstance(data, list) else [data]
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        for k, v in item.items():
            assert v is not None, f"Item {i}: field '{k}' is null"
            if isinstance(v, str):
                assert v.strip() != "", f"Item {i}: field '{k}' is empty string"

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
    path = workspace / "firewall_rules.json"
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
    consistency = dominant / len(all_keys) if all_keys else 1
    assert consistency >= 0.7, f"Key naming inconsistent: {snake} snake, {camel} camel, {pascal} pascal out of {len(all_keys)} keys"

@pytest.mark.weight(1)
def test_no_duplicate_entries(workspace):
    """Output should not contain exact duplicate rows/objects."""
    import json
    path = workspace / "firewall_rules.json"
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
    bad_patterns = [".DS_Store", "Thumbs.db", ".log", ".bak", ".tmp"]
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
