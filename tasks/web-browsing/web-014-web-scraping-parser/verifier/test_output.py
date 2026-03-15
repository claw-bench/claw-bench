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
