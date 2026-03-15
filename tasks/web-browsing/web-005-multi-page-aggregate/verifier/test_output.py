"""Verifier for web-005: Multi-Page Data Aggregation."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def aggregated(workspace):
    path = workspace / "aggregated.json"
    assert path.exists(), "aggregated.json not found"
    return json.loads(path.read_text())


def test_output_file_exists(workspace):
    assert (workspace / "aggregated.json").exists()


def test_total_products(aggregated):
    assert aggregated["total_products"] == 15


def test_products_list_length(aggregated):
    assert len(aggregated["products"]) == 15


def test_all_pages_represented(aggregated):
    pages = set(p["source_page"] for p in aggregated["products"])
    assert len(pages) == 5


def test_price_range_min(aggregated):
    assert aggregated["price_range"]["min"] == 24.99


def test_price_range_max(aggregated):
    assert aggregated["price_range"]["max"] == 599.99


def test_categories(aggregated):
    expected = ["Electronics", "Home & Kitchen", "Office", "Sports"]
    assert aggregated["categories"] == expected


def test_categories_sorted(aggregated):
    cats = aggregated["categories"]
    assert cats == sorted(cats)


def test_avg_rating_reasonable(aggregated):
    avg = aggregated["avg_rating"]
    assert 4.0 <= avg <= 5.0


def test_products_have_required_fields(aggregated):
    for p in aggregated["products"]:
        assert "name" in p
        assert "price" in p
        assert "category" in p
        assert "rating" in p
        assert "source_page" in p


def test_specific_product_present(aggregated):
    names = [p["name"] for p in aggregated["products"]]
    assert "Wireless Headphones Pro" in names
    assert "Robot Vacuum Pro" in names
    assert "Smart Water Bottle" in names
