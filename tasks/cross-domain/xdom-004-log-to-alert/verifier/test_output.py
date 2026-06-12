"""Verifier for xdom-004: Log to Alert."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def alerts(workspace):
    path = workspace / "alerts.json"
    assert path.exists(), "alerts.json not found"
    with open(path) as f:
        data = json.load(f)
    assert isinstance(data, list)
    return data


@pytest.fixture
def incident_report(workspace):
    path = workspace / "incident_report.md"
    assert path.exists(), "incident_report.md not found"
    return path.read_text()


def test_alerts_file_exists(workspace):
    """alerts.json must exist."""
    assert (workspace / "alerts.json").exists()


def test_incident_report_exists(workspace):
    """incident_report.md must exist."""
    assert (workspace / "incident_report.md").exists()


def test_three_alerts_triggered(alerts):
    """All 3 alert rules should be triggered."""
    assert len(alerts) == 3, f"Expected 3 alerts, got {len(alerts)}"


def test_alert_required_fields(alerts):
    """Each alert must have required fields."""
    required = {"rule_id", "rule_name", "severity", "message"}
    for i, alert in enumerate(alerts):
        missing = required - set(alert.keys())
        assert not missing, f"Alert {i} missing fields: {missing}"


def test_high_error_rate_alert(alerts):
    """High Error Rate alert (rule-001) must be present."""
    matches = [a for a in alerts if a.get("rule_id") == "rule-001" or "error rate" in a.get("rule_name", "").lower()]
    assert len(matches) >= 1, "High Error Rate alert not found"
    alert = matches[0]
    assert alert["severity"] in ("critical", "high")


def test_database_failure_alert(alerts):
    """Database Connection Failure alert (rule-002) must be present."""
    matches = [a for a in alerts if a.get("rule_id") == "rule-002" or "database" in a.get("rule_name", "").lower()]
    assert len(matches) >= 1, "Database Connection Failure alert not found"
    alert = matches[0]
    assert alert["severity"] == "critical"


def test_memory_threshold_alert(alerts):
    """Memory Threshold alert (rule-003) must be present."""
    matches = [a for a in alerts if a.get("rule_id") == "rule-003" or "memory" in a.get("rule_name", "").lower()]
    assert len(matches) >= 1, "Memory Threshold Exceeded alert not found"
    alert = matches[0]
    assert alert["severity"] in ("critical", "high")


def test_report_has_timeline(incident_report):
    """Incident report must have a timeline section."""
    lower = incident_report.lower()
    assert "timeline" in lower, "No timeline section in incident report"


def test_report_timeline_has_key_events(incident_report):
    """Timeline must mention key events."""
    lower = incident_report.lower()
    assert "database" in lower, "Timeline should mention database events"
    assert "memory" in lower or "gc" in lower, "Timeline should mention memory/GC events"


def test_report_has_alerts_section(incident_report):
    """Incident report must summarize the alerts."""
    lower = incident_report.lower()
    assert "alert" in lower, "No alerts section in incident report"


def test_report_has_impact_or_recommendations(incident_report):
    """Report must have impact assessment or recommended actions."""
    lower = incident_report.lower()
    has_impact = "impact" in lower
    has_recommend = "recommend" in lower or "action" in lower or "remediat" in lower
    assert has_impact or has_recommend, "Report missing impact assessment or recommendations"


def test_alert_severities_valid(alerts):
    """All alert severities must be valid values."""
    valid = {"low", "medium", "high", "critical"}
    for alert in alerts:
        assert alert["severity"] in valid, f"Invalid severity: {alert['severity']}"


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
    path = workspace / "alert_rules.json"
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
    path = workspace / "alert_rules.json"
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
    path = workspace / "alert_rules.json"
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
