"""Verifier for mem-012: Fact Extraction and Update."""

import json
import pytest
from pathlib import Path


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


def _load(workspace):
    return json.loads((workspace / "current_facts.json").read_text())


def test_file_exists(workspace):
    """current_facts.json must exist."""
    assert (workspace / "current_facts.json").exists(), "current_facts.json not found"


def test_valid_json(workspace):
    """current_facts.json must be valid JSON."""
    try:
        _load(workspace)
    except json.JSONDecodeError as e:
        pytest.fail(f"current_facts.json is not valid JSON: {e}")


def test_total_statements(workspace):
    """Must report 20 total statements."""
    data = _load(workspace)
    assert data["total_statements"] == 20, f"Expected 20 statements, got {data['total_statements']}"


def test_total_unique_facts(workspace):
    """Must report 14 unique facts."""
    data = _load(workspace)
    assert data["total_unique_facts"] == 14, f"Expected 14 unique facts, got {data['total_unique_facts']}"


def test_total_updates(workspace):
    """Must report exactly 6 updates."""
    data = _load(workspace)
    assert data["total_updates"] == 6, f"Expected 6 updates, got {data['total_updates']}"


def test_facts_is_list(workspace):
    """facts must be a list."""
    data = _load(workspace)
    assert isinstance(data["facts"], list), "facts must be a list"


def test_fact_count(workspace):
    """Must have 14 facts."""
    data = _load(workspace)
    assert len(data["facts"]) == 14, f"Expected 14 facts, got {len(data['facts'])}"


def test_alice_phone_updated(workspace):
    """Alice's phone must be updated to 555-0101."""
    data = _load(workspace)
    alice_phone = [f for f in data["facts"] if f["subject"] == "Alice" and f["attribute"] == "phone"]
    assert len(alice_phone) == 1, "Should have exactly one Alice/phone fact"
    assert alice_phone[0]["current_value"] == "555-0101", f"Expected 555-0101, got {alice_phone[0]['current_value']}"
    assert alice_phone[0]["was_updated"] is True, "Alice's phone should be marked as updated"


def test_alice_email_updated(workspace):
    """Alice's email must be updated to alice@newmail.com."""
    data = _load(workspace)
    alice_email = [f for f in data["facts"] if f["subject"] == "Alice" and f["attribute"] == "email"]
    assert len(alice_email) == 1, "Should have exactly one Alice/email fact"
    assert alice_email[0]["current_value"] == "alice@newmail.com"
    assert alice_email[0]["was_updated"] is True


def test_bob_department_updated(workspace):
    """Bob's department must be updated to Product."""
    data = _load(workspace)
    bob_dept = [f for f in data["facts"] if f["subject"] == "Bob" and f["attribute"] == "department"]
    assert len(bob_dept) == 1
    assert bob_dept[0]["current_value"] == "Product"
    assert bob_dept[0]["was_updated"] is True


def test_carol_office_updated(workspace):
    """Carol's office must be updated to Room 405."""
    data = _load(workspace)
    carol_office = [f for f in data["facts"] if f["subject"] == "Carol" and f["attribute"] == "office"]
    assert len(carol_office) == 1
    assert carol_office[0]["current_value"] == "Room 405"
    assert carol_office[0]["was_updated"] is True


def test_dave_phone_updated(workspace):
    """Dave's phone must be updated to 555-0444."""
    data = _load(workspace)
    dave_phone = [f for f in data["facts"] if f["subject"] == "Dave" and f["attribute"] == "phone"]
    assert len(dave_phone) == 1
    assert dave_phone[0]["current_value"] == "555-0444"
    assert dave_phone[0]["was_updated"] is True


def test_non_updated_facts_correct(workspace):
    """Non-updated facts must have was_updated=false."""
    data = _load(workspace)
    non_updated = [f for f in data["facts"] if not f["was_updated"]]
    assert len(non_updated) == 8, f"Expected 8 non-updated facts, got {len(non_updated)}"


def test_facts_sorted(workspace):
    """Facts must be sorted by subject then attribute."""
    data = _load(workspace)
    keys = [(f["subject"], f["attribute"]) for f in data["facts"]]
    assert keys == sorted(keys), "Facts must be sorted by subject, then attribute"


def test_fact_structure(workspace):
    """Each fact must have required keys."""
    data = _load(workspace)
    required = {"subject", "attribute", "current_value", "was_updated", "source_id"}
    for fact in data["facts"]:
        missing = required - set(fact.keys())
        assert not missing, f"Fact missing keys: {missing}"
