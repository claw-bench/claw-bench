"""Verifier for mem-015: Timeline Reconstructor."""

import json
import pytest
from pathlib import Path


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


def _load(workspace):
    return json.loads((workspace / "timeline.json").read_text())


def test_file_exists(workspace):
    assert (workspace / "timeline.json").exists(), "timeline.json not found"


def test_valid_json(workspace):
    try:
        _load(workspace)
    except json.JSONDecodeError as e:
        pytest.fail(f"timeline.json is not valid JSON: {e}")


def test_has_required_keys(workspace):
    data = _load(workspace)
    for key in ["events", "total_events", "earliest_date", "latest_date"]:
        assert key in data, f"Missing key: {key}"


def test_total_events(workspace):
    data = _load(workspace)
    assert data["total_events"] == 10, f"Expected 10 events, got {data['total_events']}"


def test_event_count(workspace):
    data = _load(workspace)
    assert len(data["events"]) == 10, f"Expected 10 events in list, got {len(data['events'])}"


def test_e1_date(workspace):
    """E1: anchor 2025-03-03."""
    data = _load(workspace)
    e1 = [e for e in data["events"] if e["id"] == "E1"][0]
    assert e1["date"] == "2025-03-03"


def test_e2_date(workspace):
    """E2: 5 days after E1 = 2025-03-08."""
    data = _load(workspace)
    e2 = [e for e in data["events"] if e["id"] == "E2"][0]
    assert e2["date"] == "2025-03-08", f"Expected 2025-03-08, got {e2['date']}"


def test_e3_date(workspace):
    """E3: 2 days after E2 = 2025-03-10."""
    data = _load(workspace)
    e3 = [e for e in data["events"] if e["id"] == "E3"][0]
    assert e3["date"] == "2025-03-10", f"Expected 2025-03-10, got {e3['date']}"


def test_e4_date(workspace):
    """E4: 1 week after E3 = 2025-03-17."""
    data = _load(workspace)
    e4 = [e for e in data["events"] if e["id"] == "E4"][0]
    assert e4["date"] == "2025-03-17", f"Expected 2025-03-17, got {e4['date']}"


def test_e5_date(workspace):
    """E5: 3 days after E4 = 2025-03-20."""
    data = _load(workspace)
    e5 = [e for e in data["events"] if e["id"] == "E5"][0]
    assert e5["date"] == "2025-03-20", f"Expected 2025-03-20, got {e5['date']}"


def test_e6_date(workspace):
    """E6: anchor 2025-03-24."""
    data = _load(workspace)
    e6 = [e for e in data["events"] if e["id"] == "E6"][0]
    assert e6["date"] == "2025-03-24"


def test_e7_date(workspace):
    """E7: 4 days after E6 = 2025-03-28."""
    data = _load(workspace)
    e7 = [e for e in data["events"] if e["id"] == "E7"][0]
    assert e7["date"] == "2025-03-28", f"Expected 2025-03-28, got {e7['date']}"


def test_e8_date(workspace):
    """E8: 1 week after E7 = 2025-04-04."""
    data = _load(workspace)
    e8 = [e for e in data["events"] if e["id"] == "E8"][0]
    assert e8["date"] == "2025-04-04", f"Expected 2025-04-04, got {e8['date']}"


def test_e9_date(workspace):
    """E9: anchor 2025-04-08."""
    data = _load(workspace)
    e9 = [e for e in data["events"] if e["id"] == "E9"][0]
    assert e9["date"] == "2025-04-08"


def test_e10_date(workspace):
    """E10: 5 days after E9 = 2025-04-13."""
    data = _load(workspace)
    e10 = [e for e in data["events"] if e["id"] == "E10"][0]
    assert e10["date"] == "2025-04-13", f"Expected 2025-04-13, got {e10['date']}"


def test_chronological_order(workspace):
    """Events must be sorted chronologically."""
    data = _load(workspace)
    dates = [e["date"] for e in data["events"]]
    assert dates == sorted(dates), f"Events not in chronological order: {dates}"


def test_earliest_date(workspace):
    data = _load(workspace)
    assert data["earliest_date"] == "2025-03-03"


def test_latest_date(workspace):
    data = _load(workspace)
    assert data["latest_date"] == "2025-04-13"


def test_event_structure(workspace):
    """Each event must have id, event, date."""
    data = _load(workspace)
    for event in data["events"]:
        assert "id" in event, "Event missing 'id'"
        assert "event" in event, "Event missing 'event'"
        assert "date" in event, "Event missing 'date'"


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
    path = workspace / "fragments.json"
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
    path = workspace / "fragments.json"
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
    path = workspace / "fragments.json"
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
