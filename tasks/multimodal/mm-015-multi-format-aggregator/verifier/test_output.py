"""Verifier for mm-015: Multi-Format Aggregator."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def dashboard(workspace):
    path = workspace / "dashboard.json"
    assert path.exists(), "dashboard.json not found in workspace"
    return json.loads(path.read_text())


def test_output_file_exists(workspace):
    assert (workspace / "dashboard.json").exists()


def test_valid_json(workspace):
    path = workspace / "dashboard.json"
    try:
        json.loads(path.read_text())
    except json.JSONDecodeError as e:
        pytest.fail(f"dashboard.json is not valid JSON: {e}")


def test_has_products_key(dashboard):
    assert "products" in dashboard, "Must have 'products' key"
    assert isinstance(dashboard["products"], list)


def test_product_count(dashboard):
    assert len(dashboard["products"]) == 5, f"Expected 5 products, got {len(dashboard['products'])}"


def test_product_names(dashboard):
    names = [p["name"] for p in dashboard["products"]]
    expected = ["Gadget X", "Gadget Y", "Gadget Z", "Widget A", "Widget B"]
    assert names == expected, f"Expected {expected}, got {names}"


def test_products_sorted(dashboard):
    names = [p["name"] for p in dashboard["products"]]
    assert names == sorted(names), "Products must be sorted alphabetically by name"


def test_product_required_fields(dashboard):
    for p in dashboard["products"]:
        assert "name" in p
        assert "total_sales" in p
        assert "total_units_sold" in p
        assert "stock_level" in p
        assert "alerts" in p
        assert isinstance(p["alerts"], list)


def test_widget_a_sales(dashboard):
    wa = next(p for p in dashboard["products"] if p["name"] == "Widget A")
    # 50*12.99 + 25*12.99 + 40*12.99 = 115*12.99 = 1493.85
    assert abs(wa["total_sales"] - 1493.85) < 0.01, f"Widget A total_sales should be 1493.85, got {wa['total_sales']}"


def test_widget_a_units(dashboard):
    wa = next(p for p in dashboard["products"] if p["name"] == "Widget A")
    assert wa["total_units_sold"] == 115, f"Widget A units sold should be 115, got {wa['total_units_sold']}"


def test_widget_b_sales(dashboard):
    wb = next(p for p in dashboard["products"] if p["name"] == "Widget B")
    # 30*24.50 + 10*24.50 + 20*24.50 = 60*24.50 = 1470.00
    assert abs(wb["total_sales"] - 1470.0) < 0.01, f"Widget B total_sales should be 1470.0, got {wb['total_sales']}"


def test_gadget_x_sales(dashboard):
    gx = next(p for p in dashboard["products"] if p["name"] == "Gadget X")
    # 20*45.00 + 35*45.00 = 55*45 = 2475.00
    assert abs(gx["total_sales"] - 2475.0) < 0.01, f"Gadget X total_sales should be 2475.0, got {gx['total_sales']}"


def test_gadget_y_sales(dashboard):
    gy = next(p for p in dashboard["products"] if p["name"] == "Gadget Y")
    # 15*33.75 + 10*33.75 = 25*33.75 = 843.75
    assert abs(gy["total_sales"] - 843.75) < 0.01, f"Gadget Y total_sales should be 843.75, got {gy['total_sales']}"


def test_gadget_z_no_sales(dashboard):
    gz = next(p for p in dashboard["products"] if p["name"] == "Gadget Z")
    assert gz["total_sales"] == 0, "Gadget Z has no sales"
    assert gz["total_units_sold"] == 0, "Gadget Z has no units sold"


def test_stock_levels(dashboard):
    stock_map = {p["name"]: p["stock_level"] for p in dashboard["products"]}
    assert stock_map["Widget A"] == 150
    assert stock_map["Widget B"] == 200
    assert stock_map["Gadget X"] == 75
    assert stock_map["Gadget Y"] == 90
    assert stock_map["Gadget Z"] == 300


def test_widget_a_alerts(dashboard):
    wa = next(p for p in dashboard["products"] if p["name"] == "Widget A")
    assert len(wa["alerts"]) == 1, f"Widget A should have 1 alert, got {len(wa['alerts'])}"
    assert "low stock" in wa["alerts"][0].lower() or "reorder" in wa["alerts"][0].lower()


def test_gadget_x_alerts(dashboard):
    gx = next(p for p in dashboard["products"] if p["name"] == "Gadget X")
    assert len(gx["alerts"]) == 1, f"Gadget X should have 1 alert, got {len(gx['alerts'])}"
    assert "returned" in gx["alerts"][0].lower() or "packaging" in gx["alerts"][0].lower()


def test_widget_b_alerts(dashboard):
    wb = next(p for p in dashboard["products"] if p["name"] == "Widget B")
    assert len(wb["alerts"]) == 1, f"Widget B should have 1 alert, got {len(wb['alerts'])}"
    assert "pricing" in wb["alerts"][0].lower() or "catalog" in wb["alerts"][0].lower()


def test_gadget_z_alerts(dashboard):
    gz = next(p for p in dashboard["products"] if p["name"] == "Gadget Z")
    assert len(gz["alerts"]) == 1, f"Gadget Z should have 1 alert, got {len(gz['alerts'])}"
    assert "promotional" in gz["alerts"][0].lower() or "not moving" in gz["alerts"][0].lower()


def test_gadget_y_no_alerts(dashboard):
    gy = next(p for p in dashboard["products"] if p["name"] == "Gadget Y")
    assert len(gy["alerts"]) == 0, f"Gadget Y should have 0 alerts, got {len(gy['alerts'])}"
