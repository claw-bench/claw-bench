"""Verifier for web-003: Extract Structured Data from Product Page."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def product(workspace):
    path = workspace / "product.json"
    assert path.exists(), "product.json not found"
    return json.loads(path.read_text())


def test_output_file_exists(workspace):
    assert (workspace / "product.json").exists()


def test_product_name(product):
    assert product["name"] == "ProDesk 5000 Electric Standing Desk"


def test_price_is_number(product):
    assert isinstance(product["price"], (int, float))
    assert product["price"] == 749.99


def test_currency(product):
    assert product["currency"] == "$"


def test_description_present(product):
    assert "premium electric standing desk" in product["description"].lower()
    assert "dual motors" in product["description"].lower()


def test_rating(product):
    assert product["rating"] == 4.7


def test_review_count(product):
    assert product["review_count"] == 1284


def test_features_count(product):
    assert len(product["features"]) == 7


def test_features_content(product):
    features_text = " ".join(product["features"]).lower()
    assert "dual motor" in features_text
    assert "warranty" in features_text
    assert "bamboo" in features_text


def test_in_stock(product):
    assert product["in_stock"] is True


def test_sku(product):
    assert "PD5000" in product["sku"]


def test_all_required_fields(product):
    required = ["name", "price", "currency", "description", "rating",
                 "review_count", "features", "in_stock", "sku"]
    for field in required:
        assert field in product, f"Missing field: {field}"
