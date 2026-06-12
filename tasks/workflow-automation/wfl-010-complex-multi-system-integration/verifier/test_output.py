"""Verifier for wfl-010: Complex Multi-System Order Processing Integration."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def batch_summary(workspace):
    """Load the batch summary."""
    path = workspace / "batch_summary.json"
    assert path.exists(), "batch_summary.json not found"
    return json.loads(path.read_text())


@pytest.fixture
def validation_errors(workspace):
    """Load the validation errors."""
    path = workspace / "validation_errors.json"
    assert path.exists(), "validation_errors.json not found"
    return json.loads(path.read_text())


def test_batch_summary_exists(workspace):
    """batch_summary.json must exist."""
    assert (workspace / "batch_summary.json").exists()


def test_validation_errors_exists(workspace):
    """validation_errors.json must exist."""
    assert (workspace / "validation_errors.json").exists()


def test_invoices_directory_exists(workspace):
    """invoices/ directory must exist."""
    assert (workspace / "invoices").is_dir()


def test_total_orders_count(batch_summary):
    """Total orders should be 15."""
    assert batch_summary["total_orders"] == 15


def test_valid_orders_count(batch_summary):
    """Valid orders should be 13 (ORD-007 invalid customer, ORD-013 zero quantity)."""
    assert batch_summary["valid_orders"] == 13


def test_invalid_orders_count(batch_summary):
    """Invalid orders should be 2."""
    assert batch_summary["invalid_orders"] == 2


def test_validation_errors_content(validation_errors):
    """Should have exactly 2 validation errors for ORD-007 and ORD-013."""
    error_ids = {e["order_id"] for e in validation_errors}
    assert "ORD-007" in error_ids, "ORD-007 should be invalid (customer C999 not found)"
    assert "ORD-013" in error_ids, "ORD-013 should be invalid (quantity is 0)"


def test_correct_number_of_invoices(workspace):
    """Should generate 13 invoice files (one per valid order)."""
    invoices_dir = workspace / "invoices"
    assert invoices_dir.is_dir()
    invoice_files = list(invoices_dir.glob("invoice_*.json"))
    assert len(invoice_files) == 13, f"Expected 13 invoices, got {len(invoice_files)}"


def test_no_invoice_for_invalid_orders(workspace):
    """No invoice should exist for ORD-007 or ORD-013."""
    assert not (workspace / "invoices" / "invoice_ORD-007.json").exists()
    assert not (workspace / "invoices" / "invoice_ORD-013.json").exists()


def test_invoice_has_required_fields(workspace):
    """Each invoice must have all required fields."""
    required = {
        "order_id", "customer_name", "customer_email", "address",
        "product", "quantity", "unit_price", "subtotal",
        "discount_pct", "discount_amount", "total", "date"
    }
    invoice_path = workspace / "invoices" / "invoice_ORD-001.json"
    assert invoice_path.exists()
    invoice = json.loads(invoice_path.read_text())
    assert required.issubset(set(invoice.keys())), (
        f"Invoice missing fields: {required - set(invoice.keys())}"
    )


def test_platinum_discount_applied(workspace):
    """ORD-001 (C001, platinum, qty=2): 15% tier, 0% volume -> 15% discount."""
    invoice = json.loads((workspace / "invoices" / "invoice_ORD-001.json").read_text())
    assert invoice["subtotal"] == 2400.0  # 2 * 1200
    assert abs(invoice["discount_pct"] - 0.15) < 0.001
    assert abs(invoice["discount_amount"] - 360.0) < 0.01
    assert abs(invoice["total"] - 2040.0) < 0.01


def test_gold_with_volume_discount(workspace):
    """ORD-002 (C002, gold, qty=15): 10% tier + 5% volume = 15% discount."""
    invoice = json.loads((workspace / "invoices" / "invoice_ORD-002.json").read_text())
    assert invoice["subtotal"] == 375.0  # 15 * 25
    assert abs(invoice["discount_pct"] - 0.15) < 0.001
    assert abs(invoice["total"] - 318.75) < 0.01


def test_silver_with_large_volume_discount(workspace):
    """ORD-011 (C003, silver, qty=55): 5% tier + 10% volume = 15% discount."""
    invoice = json.loads((workspace / "invoices" / "invoice_ORD-011.json").read_text())
    assert invoice["subtotal"] == 990.0  # 55 * 18
    assert abs(invoice["discount_pct"] - 0.15) < 0.001
    assert abs(invoice["total"] - 841.5) < 0.01


def test_bronze_no_discount(workspace):
    """ORD-006 (C005, bronze, qty=3): 0% tier + 0% volume = 0% discount."""
    invoice = json.loads((workspace / "invoices" / "invoice_ORD-006.json").read_text())
    assert invoice["subtotal"] == 195.0  # 3 * 65
    assert abs(invoice["discount_pct"] - 0.0) < 0.001
    assert abs(invoice["total"] - 195.0) < 0.01


def test_total_revenue(batch_summary):
    """Total revenue should be approximately 9411.25."""
    assert abs(batch_summary["total_revenue"] - 9411.25) < 0.01


def test_total_discount(batch_summary):
    """Total discount should be approximately 1378.75."""
    assert abs(batch_summary["total_discount"] - 1378.75) < 0.01


def test_orders_by_tier(batch_summary):
    """Orders by tier must match expected distribution."""
    tiers = batch_summary["orders_by_tier"]
    assert tiers.get("platinum") == 4  # C001 has 3 orders + C007 has 1
    assert tiers.get("gold") == 3     # C002 has 2 + C004 has 1
    assert tiers.get("silver") == 4   # C003 has 2 + C006 has 2
    assert tiers.get("bronze") == 2   # C005 has 1 + C008 has 1


def test_top_customer(batch_summary):
    """Top customer by total spend should be C001 (Acme Corporation)."""
    assert batch_summary["top_customer"] == "C001"


def test_average_order_value(batch_summary):
    """Average order value should be approximately 723.94."""
    assert abs(batch_summary["average_order_value"] - 723.94) < 0.01


def test_customer_enrichment_in_invoice(workspace):
    """Invoice should contain correct customer data from enrichment."""
    invoice = json.loads((workspace / "invoices" / "invoice_ORD-001.json").read_text())
    assert invoice["customer_name"] == "Acme Corporation"
    assert invoice["customer_email"] == "orders@acme.com"
    assert "New York" in invoice["address"]


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
    path = workspace / "customers.json"
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
    path = workspace / "customers.json"
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
    path = workspace / "orders.csv"
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
