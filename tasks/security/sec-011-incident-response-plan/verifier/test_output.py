"""Verifier for sec-011: Incident Response Plan."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def response_plan(workspace):
    """Load and return the response plan markdown."""
    path = workspace / "response_plan.md"
    assert path.exists(), "response_plan.md not found in workspace"
    return path.read_text()


@pytest.fixture
def timeline(workspace):
    """Load and return the timeline JSON."""
    path = workspace / "timeline.json"
    assert path.exists(), "timeline.json not found in workspace"
    data = json.loads(path.read_text())
    assert isinstance(data, list), "timeline.json must contain a JSON array"
    return data


def test_response_plan_exists(workspace):
    """response_plan.md must exist."""
    assert (workspace / "response_plan.md").exists()


def test_timeline_exists(workspace):
    """timeline.json must exist."""
    assert (workspace / "timeline.json").exists()


def test_plan_has_incident_summary(response_plan):
    """Response plan must include an incident summary section."""
    lower = response_plan.lower()
    assert "summary" in lower or "incident" in lower


def test_plan_references_affected_systems(response_plan):
    """Response plan must reference the affected systems."""
    assert "app-srv-03" in response_plan or "app_srv_03" in response_plan
    assert "db-primary" in response_plan or "db_primary" in response_plan or "database" in response_plan.lower()


def test_plan_references_correct_playbook(response_plan):
    """Response plan must reference the data breach playbook (PB-002)."""
    lower = response_plan.lower()
    assert "pb-002" in lower or "data breach" in lower or "breach response" in lower


def test_plan_has_containment_steps(response_plan):
    """Response plan must include containment/immediate actions."""
    lower = response_plan.lower()
    assert "contain" in lower or "immediate" in lower or "isolat" in lower


def test_plan_has_communication_section(response_plan):
    """Response plan must include a communication plan."""
    lower = response_plan.lower()
    assert "communicat" in lower or "notif" in lower or "legal" in lower


def test_plan_mentions_credential_revocation(response_plan):
    """Response plan must mention revoking compromised credentials."""
    lower = response_plan.lower()
    assert "revok" in lower or "disable" in lower or "reset" in lower or "credential" in lower


def test_timeline_has_minimum_events(timeline):
    """Timeline must include at least the 5 known events plus response milestones."""
    assert len(timeline) >= 7, f"Expected at least 7 timeline events, got {len(timeline)}"


def test_timeline_events_have_required_fields(timeline):
    """Each timeline event must have timestamp, event, source."""
    for entry in timeline:
        assert "timestamp" in entry, "Missing 'timestamp' field"
        assert "event" in entry, "Missing 'event' field"
        assert "source" in entry, "Missing 'source' field"


def test_timeline_includes_initial_compromise(timeline):
    """Timeline must include the initial authentication event at 08:15."""
    events_text = " ".join(e["event"] for e in timeline).lower()
    assert "08:15" in " ".join(e["timestamp"] for e in timeline) or "authenticat" in events_text


def test_timeline_includes_data_exfiltration(timeline):
    """Timeline must include the data transfer spike."""
    events_text = " ".join(e["event"] for e in timeline).lower()
    assert "transfer" in events_text or "exfiltrat" in events_text or "2.3" in events_text or "outbound" in events_text


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
    path = workspace / "incident.json"
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
    path = workspace / "incident.json"
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
    path = workspace / "incident.json"
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
