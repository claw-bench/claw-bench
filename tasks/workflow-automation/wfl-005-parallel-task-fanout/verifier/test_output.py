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
    path = workspace / "aggregated_results.json"
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
    path = workspace / "aggregated_results.json"
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
    path = workspace / "aggregated_results.json"
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
