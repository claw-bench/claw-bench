"""Verifier for xdom-006: CSV Data Pipeline with Notifications."""

import csv
import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def output_csv(workspace):
    path = workspace / "output.csv"
    assert path.exists(), "output.csv not found"
    with open(path) as f:
        reader = csv.DictReader(f)
        return list(reader)


@pytest.fixture
def aggregation(workspace):
    path = workspace / "aggregation.json"
    assert path.exists(), "aggregation.json not found"
    with open(path) as f:
        return json.load(f)


@pytest.fixture
def notification(workspace):
    path = workspace / "notification.json"
    assert path.exists(), "notification.json not found"
    with open(path) as f:
        return json.load(f)


def test_output_csv_exists(workspace):
    """output.csv must exist."""
    assert (workspace / "output.csv").exists()


def test_aggregation_exists(workspace):
    """aggregation.json must exist."""
    assert (workspace / "aggregation.json").exists()


def test_notification_exists(workspace):
    """notification.json must exist."""
    assert (workspace / "notification.json").exists()


def test_output_only_completed_orders(output_csv):
    """Output should only contain completed orders (filter applied)."""
    for row in output_csv:
        assert row.get("status") == "completed", \
            f"Non-completed order found: {row.get('order_id')} status={row.get('status')}"


def test_output_row_count(output_csv):
    """Should have 24 completed orders."""
    assert len(output_csv) == 24, f"Expected 24 rows, got {len(output_csv)}"


def test_output_has_total_column(output_csv):
    """Output CSV must have a 'total' column from transform step."""
    assert "total" in output_csv[0], "Missing 'total' column in output"


def test_total_computed_correctly(output_csv):
    """The total column should equal quantity * price."""
    for row in output_csv:
        expected = float(row["quantity"]) * float(row["price"])
        actual = float(row["total"])
        assert abs(actual - expected) < 0.02, \
            f"Order {row['order_id']}: expected total {expected}, got {actual}"


def test_aggregation_has_groups(aggregation):
    """Aggregation must have groups."""
    groups = aggregation.get("groups", [])
    assert len(groups) == 3, f"Expected 3 category groups, got {len(groups)}"


def test_aggregation_categories(aggregation):
    """Aggregation must cover Electronics, Clothing, and Books."""
    groups = aggregation.get("groups", [])
    categories = {g.get("category") for g in groups}
    for cat in ["Electronics", "Clothing", "Books"]:
        assert cat in categories, f"Category '{cat}' missing from aggregation"


def test_aggregation_revenue_values(aggregation):
    """Aggregation revenue values must be approximately correct."""
    groups = aggregation.get("groups", [])
    expected = {"Electronics": 3889.76, "Clothing": 1114.84, "Books": 447.82}
    for g in groups:
        cat = g.get("category")
        if cat in expected:
            actual = g.get("total_revenue", 0)
            assert abs(actual - expected[cat]) < 5.0, \
                f"{cat} revenue: expected ~{expected[cat]}, got {actual}"


def test_notification_input_rows(notification):
    """Notification must report 30 input rows."""
    assert notification.get("input_rows") == 30


def test_notification_output_rows(notification):
    """Notification must report 24 output rows."""
    assert notification.get("output_rows") == 24


def test_notification_status(notification):
    """Notification status must be success."""
    assert notification.get("status") == "success"


def test_notification_has_summary(notification):
    """Notification must have a summary string."""
    summary = notification.get("summary", "")
    assert len(summary) > 10, "Summary is too short or missing"


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
    path = workspace / "pipeline_config.json"
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
    path = workspace / "pipeline_config.json"
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
    path = workspace / "input.csv"
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
