"""Verifier for wfl-005: Parallel Task Fan-Out and Aggregation."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def aggregated(workspace):
    """Load the aggregated results."""
    path = workspace / "aggregated_results.json"
    assert path.exists(), "aggregated_results.json not found"
    return json.loads(path.read_text())


def test_aggregated_file_exists(workspace):
    """aggregated_results.json must exist."""
    assert (workspace / "aggregated_results.json").exists()


def test_individual_results_exist(workspace):
    """All 5 individual result files must exist."""
    for i in range(1, 6):
        path = workspace / "results" / f"result_{i}.json"
        assert path.exists(), f"result_{i}.json not found"


def test_all_items_in_aggregated(aggregated):
    """Aggregated results must contain all 5 items."""
    assert "items" in aggregated
    assert len(aggregated["items"]) == 5


def test_all_items_have_required_fields(aggregated):
    """Each item must have valid, normalized, label, and score fields."""
    for item in aggregated["items"]:
        assert "valid" in item, f"Item {item.get('id')} missing 'valid'"
        assert "normalized" in item, f"Item {item.get('id')} missing 'normalized'"
        assert "label" in item, f"Item {item.get('id')} missing 'label'"
        assert "score" in item, f"Item {item.get('id')} missing 'score'"


def test_all_items_valid(aggregated):
    """All 5 items should be valid (they all have required fields)."""
    for item in aggregated["items"]:
        assert item["valid"] is True, f"Item {item['id']} should be valid"


def test_normalization_correct(workspace):
    """Normalized values must follow the formula: min(value/1000*100, 100)."""
    expected = {
        "item_1": 45.0,   # 450/1000*100
        "item_2": 78.0,   # 780/1000*100
        "item_3": 100.0,  # 1200/1000*100 capped at 100
        "item_4": 20.0,   # 200/1000*100
        "item_5": 65.0,   # 650/1000*100
    }
    for i in range(1, 6):
        result = json.loads((workspace / "results" / f"result_{i}.json").read_text())
        item_id = result["id"]
        assert abs(result["normalized"] - expected[item_id]) < 0.01, (
            f"Item {item_id}: expected normalized {expected[item_id]}, got {result['normalized']}"
        )


def test_labels_are_uppercase(aggregated):
    """Labels must be uppercase versions of names."""
    for item in aggregated["items"]:
        assert item["label"] == item["name"].upper(), (
            f"Item {item['id']}: label should be '{item['name'].upper()}', got '{item['label']}'"
        )


def test_scores_correct(aggregated):
    """Scores must follow: normalized * (1 + 0.1 * len(tags))."""
    expected_scores = {
        "item_1": round(45.0 * (1 + 0.1 * 3), 2),   # 45 * 1.3 = 58.5
        "item_2": round(78.0 * (1 + 0.1 * 2), 2),   # 78 * 1.2 = 93.6
        "item_3": round(100.0 * (1 + 0.1 * 4), 2),  # 100 * 1.4 = 140.0
        "item_4": round(20.0 * (1 + 0.1 * 1), 2),   # 20 * 1.1 = 22.0
        "item_5": round(65.0 * (1 + 0.1 * 3), 2),   # 65 * 1.3 = 84.5
    }
    for item in aggregated["items"]:
        exp = expected_scores[item["id"]]
        assert abs(item["score"] - exp) < 0.01, (
            f"Item {item['id']}: expected score {exp}, got {item['score']}"
        )


def test_summary_fields(aggregated):
    """Summary must have all required fields."""
    summary = aggregated.get("summary", {})
    assert summary.get("total_items") == 5
    assert summary.get("valid_count") == 5
    assert "total_score" in summary
    assert "average_score" in summary
    assert "highest_scorer" in summary


def test_highest_scorer_correct(aggregated):
    """Highest scorer should be item_3 (score 140.0)."""
    summary = aggregated.get("summary", {})
    assert summary.get("highest_scorer") == "item_3", (
        f"Expected highest_scorer 'item_3', got '{summary.get('highest_scorer')}'"
    )


def test_summary_total_score(aggregated):
    """Total score should be the sum of all individual scores."""
    items = aggregated["items"]
    computed_total = round(sum(item["score"] for item in items), 2)
    summary_total = aggregated["summary"]["total_score"]
    assert abs(summary_total - computed_total) < 0.01, (
        f"Expected total score {computed_total}, got {summary_total}"
    )
