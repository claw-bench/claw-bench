"""Verifier for wfl-006: Event-Driven Workflow."""

import json
from collections import Counter
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def actions_log(workspace):
    """Load the actions log."""
    path = workspace / "actions_log.json"
    assert path.exists(), "actions_log.json not found"
    return json.loads(path.read_text())


@pytest.fixture
def events(workspace):
    """Load original events."""
    return json.loads((workspace / "events.json").read_text())


@pytest.fixture
def rules(workspace):
    """Load original rules."""
    return json.loads((workspace / "rules.json").read_text())


def test_actions_log_exists(workspace):
    """actions_log.json must exist."""
    assert (workspace / "actions_log.json").exists()


def test_has_actions_and_summary(actions_log):
    """Log must have 'actions' and 'summary' keys."""
    assert "actions" in actions_log
    assert "summary" in actions_log


def test_all_events_processed(actions_log):
    """Summary must report 10 total events."""
    assert actions_log["summary"]["total_events"] == 10


def test_critical_error_triggers_alert(actions_log):
    """Critical errors (evt_02, evt_06) must trigger send_alert."""
    alert_actions = [
        a for a in actions_log["actions"]
        if a["action"] == "send_alert"
    ]
    alert_event_ids = {a["event_id"] for a in alert_actions}
    assert "evt_02" in alert_event_ids, "evt_02 should trigger send_alert"
    assert "evt_06" in alert_event_ids, "evt_06 should trigger send_alert"


def test_api_errors_logged(actions_log):
    """API errors (evt_02, evt_04, evt_09) must trigger log_api_error."""
    api_actions = [
        a for a in actions_log["actions"]
        if a["action"] == "log_api_error"
    ]
    api_event_ids = {a["event_id"] for a in api_actions}
    assert "evt_02" in api_event_ids, "evt_02 should trigger log_api_error"
    assert "evt_04" in api_event_ids, "evt_04 should trigger log_api_error"
    assert "evt_09" in api_event_ids, "evt_09 should trigger log_api_error"


def test_purchase_events_tracked(actions_log):
    """Purchase events (evt_03, evt_08) must trigger track_purchase."""
    purchase_actions = [
        a for a in actions_log["actions"]
        if a["action"] == "track_purchase"
    ]
    purchase_event_ids = {a["event_id"] for a in purchase_actions}
    assert "evt_03" in purchase_event_ids
    assert "evt_08" in purchase_event_ids


def test_signup_notification(actions_log):
    """Signup event (evt_05) must trigger notify_marketing."""
    signup_actions = [
        a for a in actions_log["actions"]
        if a["action"] == "notify_marketing"
    ]
    assert any(a["event_id"] == "evt_05" for a in signup_actions)


def test_all_errors_notify_admin(actions_log):
    """All error events should trigger notify_admin (rule_6 matches type=error)."""
    admin_actions = [
        a for a in actions_log["actions"]
        if a["action"] == "notify_admin"
    ]
    admin_event_ids = {a["event_id"] for a in admin_actions}
    # 4 error events: evt_02, evt_04, evt_06, evt_09
    assert len(admin_event_ids) == 4, f"Expected 4 error events, got {len(admin_event_ids)}"


def test_events_with_no_match(actions_log):
    """Login and logout events match no rules; count should be 3."""
    # evt_01 (login/web), evt_07 (logout/web), evt_10 (login/api) match no rules
    assert actions_log["summary"]["events_with_no_match"] == 3


def test_most_triggered_rule(actions_log):
    """rule_6 (any error notify admin) should be triggered most (4 times)."""
    assert actions_log["summary"]["most_triggered_rule"] == "rule_6"


def test_total_actions_count(actions_log):
    """Verify total action count matches the actions array length."""
    assert actions_log["summary"]["total_actions_triggered"] == len(actions_log["actions"])


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
    path = workspace / "events.json"
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
    path = workspace / "events.json"
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
    path = workspace / "events.json"
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
