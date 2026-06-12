"""Verifier for mem-013: Entity Relationship Tracker."""

import json
import pytest
from pathlib import Path


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


def _load(workspace):
    return json.loads((workspace / "entity_graph.json").read_text())


def test_file_exists(workspace):
    assert (workspace / "entity_graph.json").exists(), "entity_graph.json not found"


def test_valid_json(workspace):
    try:
        _load(workspace)
    except json.JSONDecodeError as e:
        pytest.fail(f"entity_graph.json is not valid JSON: {e}")


def test_total_events(workspace):
    data = _load(workspace)
    assert data["total_events"] == 20, f"Expected 20 events, got {data['total_events']}"


def test_has_required_keys(workspace):
    data = _load(workspace)
    for key in ["teams", "people", "dissolved_teams", "total_events"]:
        assert key in data, f"Missing key: {key}"


def test_dissolved_teams(workspace):
    """Gamma and Beta should be dissolved."""
    data = _load(workspace)
    dissolved = sorted(data["dissolved_teams"])
    assert dissolved == ["Beta", "Gamma"], f"Expected ['Beta', 'Gamma'], got {dissolved}"


def test_alpha_team_members(workspace):
    """Alpha should have Alice and Frank after all events."""
    data = _load(workspace)
    alpha = data["teams"]["Alpha"]
    assert sorted(alpha["members"]) == ["Alice", "Frank"], (
        f"Expected Alpha members ['Alice', 'Frank'], got {alpha['members']}"
    )


def test_alpha_team_lead(workspace):
    """Frank was promoted to Alpha lead (event 14), replacing Alice."""
    data = _load(workspace)
    alpha = data["teams"]["Alpha"]
    assert alpha["lead"] == "Frank", f"Expected Alpha lead 'Frank', got {alpha['lead']}"


def test_alpha_active(workspace):
    data = _load(workspace)
    assert data["teams"]["Alpha"]["active"] is True


def test_delta_team_members(workspace):
    """Delta should have Bob, Carol, Dave, Eve, Grace after merges."""
    data = _load(workspace)
    delta = data["teams"]["Delta"]
    assert sorted(delta["members"]) == ["Bob", "Carol", "Dave", "Eve", "Grace"], (
        f"Expected Delta members ['Bob', 'Carol', 'Dave', 'Eve', 'Grace'], got {sorted(delta['members'])}"
    )


def test_delta_team_lead(workspace):
    """Grace was promoted to Delta lead."""
    data = _load(workspace)
    delta = data["teams"]["Delta"]
    assert delta["lead"] == "Grace", f"Expected Delta lead 'Grace', got {delta['lead']}"


def test_gamma_dissolved(workspace):
    data = _load(workspace)
    gamma = data["teams"]["Gamma"]
    assert gamma["active"] is False, "Gamma should be inactive (dissolved)"
    assert gamma["members"] == [], f"Gamma should have no members, got {gamma['members']}"


def test_beta_dissolved(workspace):
    data = _load(workspace)
    beta = data["teams"]["Beta"]
    assert beta["active"] is False, "Beta should be inactive (dissolved)"
    assert beta["members"] == [], f"Beta should have no members, got {beta['members']}"


def test_bob_history(workspace):
    """Bob: Alpha -> Beta -> Delta."""
    data = _load(workspace)
    bob = data["people"]["Bob"]
    assert bob["history"] == ["Alpha", "Beta", "Delta"], (
        f"Expected Bob history ['Alpha', 'Beta', 'Delta'], got {bob['history']}"
    )
    assert bob["current_team"] == "Delta"


def test_eve_history(workspace):
    """Eve: Gamma -> Alpha (via merge) -> left Alpha -> Delta."""
    data = _load(workspace)
    eve = data["people"]["Eve"]
    assert eve["current_team"] == "Delta"
    assert "Gamma" in eve["history"] and "Alpha" in eve["history"] and "Delta" in eve["history"]


def test_all_people_present(workspace):
    """All 7 people must be tracked."""
    data = _load(workspace)
    expected = {"Alice", "Bob", "Carol", "Dave", "Eve", "Frank", "Grace"}
    actual = set(data["people"].keys())
    assert expected == actual, f"Expected people {expected}, got {actual}"


def test_all_teams_present(workspace):
    """All 4 teams must be tracked."""
    data = _load(workspace)
    expected = {"Alpha", "Beta", "Gamma", "Delta"}
    actual = set(data["teams"].keys())
    assert expected == actual, f"Expected teams {expected}, got {actual}"


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
    path = workspace / "entity_graph.json"
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
    path = workspace / "entity_graph.json"
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
    path = workspace / "entity_graph.json"
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
