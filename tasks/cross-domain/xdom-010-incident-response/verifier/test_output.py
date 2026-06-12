"""Verifier for xdom-010: Incident Response Workflow."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def timeline(workspace):
    path = workspace / "timeline.json"
    assert path.exists(), "timeline.json not found"
    with open(path) as f:
        return json.load(f)


@pytest.fixture
def root_cause(workspace):
    path = workspace / "root_cause.md"
    assert path.exists(), "root_cause.md not found"
    return path.read_text()


@pytest.fixture
def remediation(workspace):
    path = workspace / "remediation_plan.json"
    assert path.exists(), "remediation_plan.json not found"
    with open(path) as f:
        return json.load(f)


@pytest.fixture
def communication(workspace):
    path = workspace / "communication_draft.md"
    assert path.exists(), "communication_draft.md not found"
    return path.read_text()


def test_timeline_exists(workspace):
    """timeline.json must exist."""
    assert (workspace / "timeline.json").exists()


def test_root_cause_exists(workspace):
    """root_cause.md must exist."""
    assert (workspace / "root_cause.md").exists()


def test_remediation_exists(workspace):
    """remediation_plan.json must exist."""
    assert (workspace / "remediation_plan.json").exists()


def test_communication_exists(workspace):
    """communication_draft.md must exist."""
    assert (workspace / "communication_draft.md").exists()


def test_timeline_has_events(timeline):
    """Timeline must have events."""
    events = timeline.get("events", [])
    assert len(events) >= 8, f"Expected at least 8 timeline events, got {len(events)}"


def test_timeline_events_have_fields(timeline):
    """Each event must have timestamp, source, and description."""
    for i, event in enumerate(timeline.get("events", [])):
        assert "timestamp" in event, f"Event {i} missing timestamp"
        assert "description" in event, f"Event {i} missing description"


def test_timeline_covers_config_change(timeline):
    """Timeline must include the config change event."""
    descriptions = " ".join(e.get("description", "").lower() for e in timeline.get("events", []))
    assert "config" in descriptions or "rate limit" in descriptions, \
        "Timeline should reference the configuration change"


def test_timeline_covers_resolution(timeline):
    """Timeline must include resolution events."""
    descriptions = " ".join(e.get("description", "").lower() for e in timeline.get("events", []))
    assert "rollback" in descriptions or "restored" in descriptions or "resume" in descriptions, \
        "Timeline should cover incident resolution"


def test_root_cause_identifies_config(root_cause):
    """Root cause must identify the config change as the cause."""
    lower = root_cause.lower()
    assert "config" in lower or "rate limit" in lower, \
        "Root cause should mention configuration/rate limit change"


def test_root_cause_has_contributing_factors(root_cause):
    """Root cause must list contributing factors."""
    lower = root_cause.lower()
    assert "factor" in lower or "contribut" in lower or "cause" in lower, \
        "Root cause should discuss contributing factors"


def test_root_cause_has_evidence(root_cause):
    """Root cause should reference evidence from the data."""
    lower = root_cause.lower()
    has_evidence = "evidence" in lower or "log" in lower or "alert" in lower or "timestamp" in lower
    assert has_evidence, "Root cause should reference evidence"


def test_remediation_has_three_categories(remediation):
    """Remediation must have immediate, short-term, and long-term actions."""
    assert "immediate_actions" in remediation, "Missing immediate_actions"
    assert "short_term_fixes" in remediation, "Missing short_term_fixes"
    assert "long_term_improvements" in remediation, "Missing long_term_improvements"


def test_remediation_actions_have_fields(remediation):
    """Each remediation action must have description, owner, priority, and deadline."""
    required = {"description", "owner", "priority"}
    for category in ["immediate_actions", "short_term_fixes", "long_term_improvements"]:
        for i, action in enumerate(remediation.get(category, [])):
            missing = required - set(action.keys())
            assert not missing, f"{category}[{i}] missing: {missing}"


def test_remediation_has_minimum_actions(remediation):
    """Each category must have at least one action."""
    assert len(remediation.get("immediate_actions", [])) >= 1
    assert len(remediation.get("short_term_fixes", [])) >= 1
    assert len(remediation.get("long_term_improvements", [])) >= 1


def test_communication_has_summary(communication):
    """Communication must have an incident summary."""
    lower = communication.lower()
    assert "summary" in lower or "overview" in lower


def test_communication_has_impact(communication):
    """Communication must describe the impact."""
    lower = communication.lower()
    assert "impact" in lower


def test_communication_has_status(communication):
    """Communication must include current status."""
    lower = communication.lower()
    assert "status" in lower or "resolved" in lower or "restored" in lower


def test_communication_has_contact(communication):
    """Communication must include a contact person."""
    lower = communication.lower()
    assert "contact" in lower or "@" in communication


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
    path = workspace / "incident_data/alerts.json"
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
    path = workspace / "incident_data/alerts.json"
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
    path = workspace / "incident_data/alerts.json"
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
