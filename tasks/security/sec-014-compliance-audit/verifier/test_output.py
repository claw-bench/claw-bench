"""Verifier for sec-014: Compliance Audit."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def report(workspace):
    """Load and return the compliance report JSON."""
    path = workspace / "compliance_report.json"
    assert path.exists(), "compliance_report.json not found in workspace"
    data = json.loads(path.read_text())
    return data


# Expected results for key rules
EXPECTED_PASS = [
    "SEC-001", "SEC-002", "SEC-004", "AUTH-002",
    "DATA-001", "DATA-002", "DATA-004",
    "LOG-001", "LOG-002", "LOG-004", "NET-001",
]

EXPECTED_FAIL = [
    "SEC-003",   # HSTS max_age too low
    "AUTH-001",  # min password length 8 < 12
    "AUTH-003",  # session timeout 60 > 30
    "AUTH-004",  # lockout attempts 10 > 5
    "AUTH-005",  # require_special is false
    "DATA-003",  # backup not encrypted
    "LOG-003",   # log integrity disabled
    "NET-002",   # default policy is allow
    "NET-003",   # SSH password auth enabled
]


def _find_result(report, rule_id):
    """Find a result by rule_id."""
    for r in report.get("results", []):
        if r.get("rule_id") == rule_id:
            return r
    return None


def test_report_file_exists(workspace):
    """compliance_report.json must exist."""
    assert (workspace / "compliance_report.json").exists()


def test_all_20_rules_checked(report):
    """All 20 rules must be checked."""
    results = report.get("results", [])
    assert len(results) == 20, f"Expected 20 results, got {len(results)}"


def test_total_rules_count(report):
    """Report total_rules must be 20."""
    assert report.get("total_rules") == 20


def test_passed_and_failed_sum(report):
    """passed + failed must equal total_rules."""
    assert report.get("passed", 0) + report.get("failed", 0) == 20


def test_known_pass_rules(report):
    """Rules that should pass must be marked pass."""
    for rule_id in EXPECTED_PASS:
        result = _find_result(report, rule_id)
        assert result is not None, f"Rule {rule_id} not found in results"
        assert result["status"] == "pass", (
            f"Rule {rule_id} should pass but got {result['status']}"
        )


def test_known_fail_rules(report):
    """Rules that should fail must be marked fail."""
    for rule_id in EXPECTED_FAIL:
        result = _find_result(report, rule_id)
        assert result is not None, f"Rule {rule_id} not found in results"
        assert result["status"] == "fail", (
            f"Rule {rule_id} should fail but got {result['status']}"
        )


def test_each_result_has_required_fields(report):
    """Each result must have rule_id, status, evidence, config_file."""
    for r in report.get("results", []):
        assert "rule_id" in r, "Missing 'rule_id'"
        assert "status" in r, "Missing 'status'"
        assert "evidence" in r, "Missing 'evidence'"
        assert "config_file" in r, "Missing 'config_file'"


def test_evidence_is_specific(report):
    """Evidence must reference specific values (not just pass/fail)."""
    for r in report.get("results", []):
        evidence = r.get("evidence", "")
        assert len(evidence) > 15, (
            f"Evidence too vague for {r['rule_id']}: '{evidence}'"
        )


def test_password_length_evidence(report):
    """AUTH-001 failure evidence must mention the actual value (8) and required value (12)."""
    result = _find_result(report, "AUTH-001")
    assert result is not None
    evidence = result.get("evidence", "")
    assert "8" in evidence and "12" in evidence, (
        f"AUTH-001 evidence should reference values 8 and 12: '{evidence}'"
    )


def test_backup_encryption_evidence(report):
    """DATA-003 failure evidence must mention backups are not encrypted."""
    result = _find_result(report, "DATA-003")
    assert result is not None
    evidence = result.get("evidence", "").lower()
    assert "false" in evidence or "not encrypted" in evidence or "encrypt" in evidence


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
    path = workspace / "compliance_rules.json"
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
    path = workspace / "compliance_rules.json"
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
    path = workspace / "compliance_rules.json"
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
