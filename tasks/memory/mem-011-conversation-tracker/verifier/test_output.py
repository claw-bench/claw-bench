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
    path = workspace / "context_map.json"
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
    path = workspace / "context_map.json"
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
    path = workspace / "context_map.json"
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
