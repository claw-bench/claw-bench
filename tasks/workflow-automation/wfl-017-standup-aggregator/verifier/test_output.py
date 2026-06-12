"""Verifier for wfl-017: Aggregate Team Standup Updates."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def team_summary(workspace):
    """Read and return the team_summary.json contents."""
    path = workspace / "team_summary.json"
    assert path.exists(), "team_summary.json not found in workspace"
    return json.loads(path.read_text())


def test_team_summary_exists(workspace):
    """team_summary.json must exist in the workspace."""
    assert (workspace / "team_summary.json").exists()


def test_date(team_summary):
    """Date should be 2026-03-12."""
    assert team_summary["date"] == "2026-03-12"


def test_team_size(team_summary):
    """Team size should be 4."""
    assert team_summary["team_size"] == 4


def test_total_completed(team_summary):
    """Total completed items should be 7 (Alice:2 + Bob:2 + Carol:1 + Dave:2)."""
    assert team_summary["total_completed"] == 7


def test_total_in_progress(team_summary):
    """Total in-progress items should be 5 (Alice:1 + Bob:1 + Carol:2 + Dave:1)."""
    assert team_summary["total_in_progress"] == 5


def test_total_blockers(team_summary):
    """Total blockers should be 3 (Alice:1 + Carol:1 + Dave:1)."""
    assert team_summary["total_blockers"] == 3


def test_members_count(team_summary):
    """Members list should have 4 entries."""
    assert len(team_summary["members"]) == 4


def test_member_names(team_summary):
    """All four team members should be listed."""
    names = {m["name"] for m in team_summary["members"]}
    assert names == {"Alice", "Bob", "Carol", "Dave"}


def test_bob_not_blocked(team_summary):
    """Bob should not be blocked."""
    bob = next(m for m in team_summary["members"] if m["name"] == "Bob")
    assert bob["blocked"] is False


def test_alice_blocked(team_summary):
    """Alice should be blocked."""
    alice = next(m for m in team_summary["members"] if m["name"] == "Alice")
    assert alice["blocked"] is True


def test_carol_blocked(team_summary):
    """Carol should be blocked."""
    carol = next(m for m in team_summary["members"] if m["name"] == "Carol")
    assert carol["blocked"] is True


def test_dave_blocked(team_summary):
    """Dave should be blocked."""
    dave = next(m for m in team_summary["members"] if m["name"] == "Dave")
    assert dave["blocked"] is True


def test_alice_completed_count(team_summary):
    """Alice should have 2 completed items."""
    alice = next(m for m in team_summary["members"] if m["name"] == "Alice")
    assert alice["completed_count"] == 2


def test_bob_completed_count(team_summary):
    """Bob should have 2 completed items."""
    bob = next(m for m in team_summary["members"] if m["name"] == "Bob")
    assert bob["completed_count"] == 2


def test_carol_completed_count(team_summary):
    """Carol should have 1 completed item."""
    carol = next(m for m in team_summary["members"] if m["name"] == "Carol")
    assert carol["completed_count"] == 1


def test_dependencies_count(team_summary):
    """Should have 2 cross-team dependencies."""
    assert len(team_summary["dependencies"]) == 2


def test_dependency_alice_to_bob(team_summary):
    """Alice depends on Bob for Stripe API keys."""
    deps = team_summary["dependencies"]
    alice_bob = [d for d in deps if d["from"] == "Alice" and d["to"] == "Bob"]
    assert len(alice_bob) == 1
    assert "stripe" in alice_bob[0]["item"].lower() or "api key" in alice_bob[0]["item"].lower()


def test_dependency_carol_to_alice(team_summary):
    """Carol depends on Alice for user profile API."""
    deps = team_summary["dependencies"]
    carol_alice = [d for d in deps if d["from"] == "Carol" and d["to"] == "Alice"]
    assert len(carol_alice) == 1
    assert "api" in carol_alice[0]["item"].lower()


def test_unresolved_blockers_count(team_summary):
    """Should have 3 unresolved blockers."""
    assert len(team_summary["unresolved_blockers"]) == 3


def test_unresolved_blockers_content(team_summary):
    """Unresolved blockers should contain entries from Alice, Carol, and Dave."""
    blockers = team_summary["unresolved_blockers"]
    blocker_text = " ".join(blockers).lower()
    assert "alice" in blocker_text
    assert "carol" in blocker_text
    assert "dave" in blocker_text


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
    path = workspace / "team_summary.json"
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
    path = workspace / "team_summary.json"
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
    path = workspace / "team_summary.json"
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
