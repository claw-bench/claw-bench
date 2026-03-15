"""Verifier for mem-011: Conversation Tracker."""

import json
import pytest
from pathlib import Path


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


def test_context_map_exists(workspace):
    """context_map.json must exist."""
    assert (workspace / "context_map.json").exists(), "context_map.json not found"


def test_context_map_valid_json(workspace):
    """context_map.json must be valid JSON."""
    content = (workspace / "context_map.json").read_text()
    try:
        json.loads(content)
    except json.JSONDecodeError as e:
        pytest.fail(f"context_map.json is not valid JSON: {e}")


def test_total_messages(workspace):
    """Must report correct total message count."""
    data = json.loads((workspace / "context_map.json").read_text())
    assert "total_messages" in data, "Missing 'total_messages' key"
    assert data["total_messages"] == 15, f"Expected 15 messages, got {data['total_messages']}"


def test_speakers_identified(workspace):
    """Must identify all three speakers."""
    data = json.loads((workspace / "context_map.json").read_text())
    assert "speakers" in data, "Missing 'speakers' key"
    speakers = set(data["speakers"])
    assert {"Alice", "Bob", "Carol"} == speakers, f"Expected Alice, Bob, Carol; got {speakers}"


def test_references_is_list(workspace):
    """references must be a list."""
    data = json.loads((workspace / "context_map.json").read_text())
    assert "references" in data, "Missing 'references' key"
    assert isinstance(data["references"], list), "references must be a list"


def test_minimum_references_count(workspace):
    """Must identify at least 7 references."""
    data = json.loads((workspace / "context_map.json").read_text())
    refs = data["references"]
    assert len(refs) >= 7, f"Expected at least 7 references, found {len(refs)}"


def test_reference_structure(workspace):
    """Each reference must have required keys."""
    data = json.loads((workspace / "context_map.json").read_text())
    required_keys = {"source_id", "referencing_id", "referencing_speaker", "context_type"}
    for ref in data["references"]:
        missing = required_keys - set(ref.keys())
        assert not missing, f"Reference missing keys: {missing}"


def test_valid_context_types(workspace):
    """All context_type values must be valid."""
    data = json.loads((workspace / "context_map.json").read_text())
    valid_types = {"quote", "recall", "response", "correction"}
    for ref in data["references"]:
        assert ref["context_type"] in valid_types, (
            f"Invalid context_type '{ref['context_type']}', expected one of {valid_types}"
        )


def test_deadline_recall_detected(workspace):
    """Must detect Bob referencing Alice's deadline mention (msg 5 -> msg 1)."""
    data = json.loads((workspace / "context_map.json").read_text())
    refs = data["references"]
    found = any(
        r["source_id"] == 1 and r["referencing_id"] == 5
        for r in refs
    )
    assert found, "Missing reference: msg 5 (Bob) should reference msg 1 (Alice's deadline)"


def test_deadline_correction_detected(workspace):
    """Must detect Alice correcting the deadline (msg 10 -> msg 1)."""
    data = json.loads((workspace / "context_map.json").read_text())
    refs = data["references"]
    found = any(
        r["source_id"] == 1 and r["referencing_id"] == 10 and r["context_type"] == "correction"
        for r in refs
    )
    assert found, "Missing reference: msg 10 should correct msg 1 (deadline change)"


def test_backend_quote_detected(workspace):
    """Must detect Bob quoting Alice's Python choice (msg 8 -> msg 4)."""
    data = json.loads((workspace / "context_map.json").read_text())
    refs = data["references"]
    found = any(
        r["source_id"] == 4 and r["referencing_id"] == 8
        for r in refs
    )
    assert found, "Missing reference: msg 8 (Bob) should reference msg 4 (Alice's Python choice)"


def test_vue_correction_detected(workspace):
    """Must detect Bob correcting Carol about Vue vs React (msg 14 -> msg 6)."""
    data = json.loads((workspace / "context_map.json").read_text())
    refs = data["references"]
    found = any(
        r["source_id"] == 6 and r["referencing_id"] == 14 and r["context_type"] == "correction"
        for r in refs
    )
    assert found, "Missing reference: msg 14 should correct msg 6 (Vue not React)"


def test_has_multiple_context_types(workspace):
    """Must use at least 3 different context types."""
    data = json.loads((workspace / "context_map.json").read_text())
    types_used = set(r["context_type"] for r in data["references"])
    assert len(types_used) >= 3, f"Expected at least 3 context types, found {types_used}"
