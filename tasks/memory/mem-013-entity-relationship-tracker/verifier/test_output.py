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
