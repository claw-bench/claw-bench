"""Verifier for mm-010: Database Schema Documentation."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def schema_docs(workspace):
    path = workspace / "schema_docs.json"
    assert path.exists(), "schema_docs.json not found in workspace"
    return json.loads(path.read_text())


def test_output_file_exists(workspace):
    assert (workspace / "schema_docs.json").exists()


def test_valid_json(workspace):
    path = workspace / "schema_docs.json"
    try:
        json.loads(path.read_text())
    except json.JSONDecodeError as e:
        pytest.fail(f"schema_docs.json is not valid JSON: {e}")


def test_top_level_structure(schema_docs):
    assert "tables" in schema_docs, "Must have 'tables' key"
    assert isinstance(schema_docs["tables"], list)


def test_table_count(schema_docs):
    assert len(schema_docs["tables"]) == 6, "Expected 6 tables"


def test_table_names(schema_docs):
    names = [t["name"] for t in schema_docs["tables"]]
    expected = ["customers", "categories", "products", "orders", "order_items", "reviews"]
    assert names == expected, f"Expected table order {expected}, got {names}"


def test_table_has_required_keys(schema_docs):
    for table in schema_docs["tables"]:
        assert "name" in table
        assert "columns" in table
        assert "foreign_keys" in table
        assert isinstance(table["columns"], list)
        assert isinstance(table["foreign_keys"], list)


def test_column_has_required_keys(schema_docs):
    for table in schema_docs["tables"]:
        for col in table["columns"]:
            assert "name" in col, f"Column missing 'name' in {table['name']}"
            assert "type" in col, f"Column missing 'type' in {table['name']}"
            assert "nullable" in col, f"Column missing 'nullable' in {table['name']}"
            assert "primary_key" in col, f"Column missing 'primary_key' in {table['name']}"


def test_customers_columns(schema_docs):
    customers = schema_docs["tables"][0]
    assert customers["name"] == "customers"
    col_names = [c["name"] for c in customers["columns"]]
    expected = ["id", "email", "first_name", "last_name", "phone", "created_at", "is_active"]
    assert col_names == expected


def test_customers_id_is_pk(schema_docs):
    customers = schema_docs["tables"][0]
    id_col = customers["columns"][0]
    assert id_col["name"] == "id"
    assert id_col["primary_key"] is True
    assert id_col["nullable"] is False


def test_customers_nullable_columns(schema_docs):
    customers = schema_docs["tables"][0]
    col_map = {c["name"]: c for c in customers["columns"]}
    assert col_map["email"]["nullable"] is False
    assert col_map["phone"]["nullable"] is True
    assert col_map["first_name"]["nullable"] is False


def test_customers_types(schema_docs):
    customers = schema_docs["tables"][0]
    col_map = {c["name"]: c for c in customers["columns"]}
    assert "INTEGER" in col_map["id"]["type"].upper()
    assert "VARCHAR" in col_map["email"]["type"].upper()
    assert "TIMESTAMP" in col_map["created_at"]["type"].upper()


def test_categories_self_referencing_fk(schema_docs):
    categories = schema_docs["tables"][1]
    assert len(categories["foreign_keys"]) == 1
    fk = categories["foreign_keys"][0]
    assert fk["column"] == "parent_id"
    assert fk["references_table"] == "categories"
    assert fk["references_column"] == "id"


def test_products_columns_count(schema_docs):
    products = schema_docs["tables"][2]
    assert len(products["columns"]) == 10


def test_products_foreign_key(schema_docs):
    products = schema_docs["tables"][2]
    assert len(products["foreign_keys"]) == 1
    fk = products["foreign_keys"][0]
    assert fk["column"] == "category_id"
    assert fk["references_table"] == "categories"


def test_products_nullable_description(schema_docs):
    products = schema_docs["tables"][2]
    col_map = {c["name"]: c for c in products["columns"]}
    assert col_map["description"]["nullable"] is True
    assert col_map["price"]["nullable"] is False


def test_orders_foreign_key(schema_docs):
    orders = schema_docs["tables"][3]
    fks = orders["foreign_keys"]
    assert len(fks) == 1
    assert fks[0]["column"] == "customer_id"
    assert fks[0]["references_table"] == "customers"


def test_order_items_two_foreign_keys(schema_docs):
    order_items = schema_docs["tables"][4]
    fks = order_items["foreign_keys"]
    assert len(fks) == 2
    fk_cols = {fk["column"] for fk in fks}
    assert "order_id" in fk_cols
    assert "product_id" in fk_cols


def test_order_items_fk_references(schema_docs):
    order_items = schema_docs["tables"][4]
    fk_map = {fk["column"]: fk for fk in order_items["foreign_keys"]}
    assert fk_map["order_id"]["references_table"] == "orders"
    assert fk_map["product_id"]["references_table"] == "products"


def test_reviews_foreign_keys(schema_docs):
    reviews = schema_docs["tables"][5]
    fks = reviews["foreign_keys"]
    assert len(fks) == 2
    fk_map = {fk["column"]: fk for fk in fks}
    assert fk_map["product_id"]["references_table"] == "products"
    assert fk_map["customer_id"]["references_table"] == "customers"


def test_reviews_nullable_columns(schema_docs):
    reviews = schema_docs["tables"][5]
    col_map = {c["name"]: c for c in reviews["columns"]}
    assert col_map["rating"]["nullable"] is False
    assert col_map["title"]["nullable"] is True
    assert col_map["body"]["nullable"] is True


def test_no_foreign_keys_on_customers(schema_docs):
    customers = schema_docs["tables"][0]
    assert len(customers["foreign_keys"]) == 0


def test_all_ids_are_primary_keys(schema_docs):
    for table in schema_docs["tables"]:
        id_col = next((c for c in table["columns"] if c["name"] == "id"), None)
        assert id_col is not None, f"Table {table['name']} must have id column"
        assert id_col["primary_key"] is True, f"id in {table['name']} must be primary key"


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
    path = workspace / "schema_docs.json"
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
    path = workspace / "schema_docs.json"
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
    path = workspace / "schema_docs.json"
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
