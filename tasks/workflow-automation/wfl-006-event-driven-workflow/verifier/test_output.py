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
