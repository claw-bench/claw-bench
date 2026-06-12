"""Verifier for wfl-015: Notification Dispatcher."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return request.config.getoption("--workspace")


@pytest.fixture
def dispatch_log(workspace):
    path = Path(workspace) / "dispatch_log.jsonl"
    assert path.exists(), "dispatch_log.jsonl not found in workspace"
    entries = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries


@pytest.fixture
def dispatch_map(dispatch_log):
    return {e["event_id"]: e for e in dispatch_log}


def test_output_file_exists(workspace):
    assert (Path(workspace) / "dispatch_log.jsonl").exists()


def test_correct_event_count(dispatch_log):
    assert len(dispatch_log) == 15, f"Expected 15 entries, got {len(dispatch_log)}"


def test_entry_structure(dispatch_log):
    for entry in dispatch_log:
        assert "event_id" in entry
        assert "matched_rules" in entry
        assert "channels" in entry
        assert isinstance(entry["matched_rules"], list)
        assert isinstance(entry["channels"], list)


def test_channels_sorted(dispatch_log):
    for entry in dispatch_log:
        assert entry["channels"] == sorted(entry["channels"]), \
            f"Channels not sorted for {entry['event_id']}"


def test_channels_deduplicated(dispatch_log):
    for entry in dispatch_log:
        assert len(entry["channels"]) == len(set(entry["channels"])), \
            f"Duplicate channels for {entry['event_id']}"


def test_critical_incident_e3(dispatch_map):
    """E3: critical incident from pagerduty - matches critical-all-channels."""
    e = dispatch_map["E3"]
    assert "critical-all-channels" in e["matched_rules"]
    for ch in ["email", "pagerduty", "slack", "sms"]:
        assert ch in e["channels"]


def test_high_alert_e2(dispatch_map):
    """E2: high alert from monitoring - matches high-severity-alerts and monitoring-medium-plus."""
    e = dispatch_map["E2"]
    assert "high-severity-alerts" in e["matched_rules"]
    assert "monitoring-medium-plus" in e["matched_rules"]
    assert "slack" in e["channels"]
    assert "pagerduty" in e["channels"]


def test_deployment_e1(dispatch_map):
    """E1: deployment low from ci-server - matches deployment-notifications only."""
    e = dispatch_map["E1"]
    assert "deployment-notifications" in e["matched_rules"]
    assert "slack" in e["channels"]
    assert "email" in e["channels"]


def test_maintenance_no_match(dispatch_map):
    """E9: maintenance low from scheduler - matches no rules."""
    e = dispatch_map["E9"]
    assert len(e["matched_rules"]) == 0
    assert len(e["channels"]) == 0


def test_maintenance_e14_no_match(dispatch_map):
    """E14: maintenance low from scheduler - matches no rules."""
    e = dispatch_map["E14"]
    assert len(e["matched_rules"]) == 0
    assert len(e["channels"]) == 0


def test_security_event_e13(dispatch_map):
    """E13: high alert from security - matches high-severity-alerts and security-events."""
    e = dispatch_map["E13"]
    assert "high-severity-alerts" in e["matched_rules"]
    assert "security-events" in e["matched_rules"]
    assert "pagerduty" in e["channels"]


def test_critical_monitoring_e7(dispatch_map):
    """E7: critical alert from monitoring - matches critical-all-channels and monitoring-medium-plus."""
    e = dispatch_map["E7"]
    assert "critical-all-channels" in e["matched_rules"]
    assert "monitoring-medium-plus" in e["matched_rules"]
    assert "sms" in e["channels"]


def test_security_incident_e15(dispatch_map):
    """E15: high incident from security - matches high-severity-alerts and security-events."""
    e = dispatch_map["E15"]
    assert "high-severity-alerts" in e["matched_rules"]
    assert "security-events" in e["matched_rules"]


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
    path = workspace / "routing_rules.json"
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
    path = workspace / "routing_rules.json"
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
    path = workspace / "routing_rules.json"
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
