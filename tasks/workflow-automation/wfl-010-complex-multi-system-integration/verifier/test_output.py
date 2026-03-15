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
