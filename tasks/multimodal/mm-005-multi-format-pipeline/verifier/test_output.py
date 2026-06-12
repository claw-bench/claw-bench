"""Verifier for mm-005: Multi-Format Data Pipeline."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def result_data(workspace):
    path = workspace / "result.json"
    assert path.exists(), "result.json not found in workspace"
    return json.loads(path.read_text())


def test_output_file_exists(workspace):
    assert (workspace / "result.json").exists()


def test_result_is_list(result_data):
    assert isinstance(result_data, list)


def test_correct_number_of_products(result_data):
    """After excluding alcohol and filtering by required tags, 7 products remain."""
    assert len(result_data) == 7


def test_excluded_category_absent(result_data):
    """Alcohol category should be excluded."""
    categories = [item["category"] for item in result_data]
    assert "alcohol" not in categories


def test_untagged_products_excluded(result_data):
    """Products without a required tag should be excluded (e.g., id=4 Steel Hammer)."""
    ids = [item["id"] for item in result_data]
    assert 4 not in ids  # Steel Hammer has no tags
    assert 8 not in ids  # Screwdriver Set has no tags


def test_sorted_by_id(result_data):
    ids = [item["id"] for item in result_data]
    assert ids == sorted(ids)


def test_widget_alpha(result_data):
    item = next(i for i in result_data if i["id"] == 1)
    assert item["name"] == "Widget Alpha"
    assert item["category"] == "electronics"
    assert item["original_price"] == 49.99
    assert item["discount_percent"] == 10
    assert item["final_price"] == 48.59
    assert "bestseller" in item["tags"]


def test_gadget_beta(result_data):
    item = next(i for i in result_data if i["id"] == 2)
    assert item["final_price"] == 145.79


def test_running_shoes(result_data):
    item = next(i for i in result_data if i["id"] == 5)
    assert item["discount_percent"] == 20
    assert item["final_price"] == 76.9


def test_usb_cable(result_data):
    item = next(i for i in result_data if i["id"] == 10)
    assert item["final_price"] == 9.71
    assert item["final_price"] >= 5.00  # min_price check


def test_winter_jacket(result_data):
    item = next(i for i in result_data if i["id"] == 9)
    assert item["final_price"] == 103.68


def test_yoga_mat_no_discount(result_data):
    item = next(i for i in result_data if i["id"] == 12)
    assert item["discount_percent"] == 0
    assert item["final_price"] == 37.8


def test_all_items_have_required_fields(result_data):
    required = {"id", "name", "category", "original_price", "discount_percent", "final_price", "tags"}
    for item in result_data:
        assert required.issubset(item.keys()), f"Missing fields in item {item.get('id')}"


def test_tags_are_lists(result_data):
    for item in result_data:
        assert isinstance(item["tags"], list)


def test_grocery_products_excluded(result_data):
    """Groceries with no required tags should be excluded."""
    ids = [item["id"] for item in result_data]
    assert 3 not in ids  # Organic Apples has tags organic,local but none are required
    assert 7 not in ids  # Canned Beans has tag budget but not required


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
    path = workspace / "discounts.json"
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
    path = workspace / "discounts.json"
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
    path = workspace / "products.csv"
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
