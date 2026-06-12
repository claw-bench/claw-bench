"""Verifier for web-014: Parse Product Table and Compute Statistics."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return request.config.getoption("--workspace")


@pytest.fixture
def data(workspace):
    path = Path(workspace) / "products.json"
    assert path.exists(), "products.json not found in workspace"
    return json.loads(path.read_text())


def test_output_file_exists(workspace):
    assert (Path(workspace) / "products.json").exists()


def test_top_level_keys(data):
    assert "products" in data
    assert "statistics" in data


def test_product_count(data):
    assert len(data["products"]) == 10


def test_product_structure(data):
    for p in data["products"]:
        assert "name" in p
        assert "price" in p
        assert "category" in p
        assert "in_stock" in p


def test_prices_are_floats(data):
    for p in data["products"]:
        assert isinstance(p["price"], (int, float))
        assert p["price"] > 0


def test_in_stock_is_boolean(data):
    for p in data["products"]:
        assert isinstance(p["in_stock"], bool)


def test_specific_products(data):
    products_by_name = {p["name"]: p for p in data["products"]}
    assert "Wireless Mouse" in products_by_name
    mouse = products_by_name["Wireless Mouse"]
    assert mouse["price"] == 29.99
    assert mouse["category"] == "Electronics"
    assert mouse["in_stock"] is True

    chair = products_by_name["Ergonomic Chair"]
    assert chair["price"] == 299.99
    assert chair["in_stock"] is False


def test_total_products(data):
    assert data["statistics"]["total_products"] == 10


def test_avg_price(data):
    # Sum: 29.99+49.95+89.99+34.50+45.00+299.99+12.99+8.49+5.99+59.99 = 636.88
    # Avg: 636.88/10 = 63.688 -> 63.69
    assert abs(data["statistics"]["avg_price"] - 63.69) < 0.01


def test_categories(data):
    cats = data["statistics"]["categories"]
    assert cats["Electronics"] == 4
    assert cats["Home Office"] == 3
    assert cats["Stationery"] == 3


def test_in_stock_count(data):
    assert data["statistics"]["in_stock_count"] == 8


def test_out_of_stock_products(data):
    out_of_stock = [p for p in data["products"] if not p["in_stock"]]
    names = {p["name"] for p in out_of_stock}
    assert "Mechanical Keyboard" in names
    assert "Ergonomic Chair" in names
    assert len(out_of_stock) == 2


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
    path = workspace / "products.json"
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
    path = workspace / "products.json"
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
    path = workspace / "products.json"
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
