"""Verifier for data-007: Join Two Datasets."""

from pathlib import Path
import csv
import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def enriched_rows(workspace):
    path = workspace / "enriched_orders.csv"
    assert path.exists(), "enriched_orders.csv not found"
    with open(path) as f:
        return list(csv.DictReader(f))


def test_enriched_file_exists(workspace):
    assert (workspace / "enriched_orders.csv").exists()


def test_all_orders_present(enriched_rows):
    assert len(enriched_rows) == 25, f"Expected 25 orders, got {len(enriched_rows)}"


def test_correct_column_count(workspace):
    path = workspace / "enriched_orders.csv"
    header = path.read_text().strip().splitlines()[0].split(",")
    assert len(header) == 7, f"Expected 7 columns, got {len(header)}"


def test_customer_info_populated(enriched_rows):
    for row in enriched_rows:
        assert row.get("name", "").strip() != "", f"Missing name for order {row['order_id']}"
        assert row.get("email", "").strip() != "", f"Missing email for order {row['order_id']}"


def test_correct_customer_mapping(enriched_rows):
    """Spot-check a few known mappings."""
    cust_map = {
        "1": "Alice Smith", "2": "Bob Jones", "3": "Carol White",
        "4": "Dave Brown", "5": "Eve Davis", "6": "Frank Miller",
        "7": "Grace Lee", "8": "Hank Wilson", "9": "Iris Taylor",
        "10": "Jack Moore"
    }
    for row in enriched_rows:
        cid = row["customer_id"]
        if cid in cust_map:
            assert row["name"] == cust_map[cid], f"Order {row['order_id']}: expected name {cust_map[cid]}, got {row['name']}"


def test_order_id_preserved(enriched_rows):
    ids = [int(row["order_id"]) for row in enriched_rows]
    assert ids == list(range(1, 26)), "Order IDs not preserved in original order"
