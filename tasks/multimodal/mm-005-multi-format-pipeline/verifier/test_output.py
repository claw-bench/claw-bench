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
