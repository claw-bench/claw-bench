"""Verifier for xdom-006: CSV Data Pipeline with Notifications."""

import csv
import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def output_csv(workspace):
    path = workspace / "output.csv"
    assert path.exists(), "output.csv not found"
    with open(path) as f:
        reader = csv.DictReader(f)
        return list(reader)


@pytest.fixture
def aggregation(workspace):
    path = workspace / "aggregation.json"
    assert path.exists(), "aggregation.json not found"
    with open(path) as f:
        return json.load(f)


@pytest.fixture
def notification(workspace):
    path = workspace / "notification.json"
    assert path.exists(), "notification.json not found"
    with open(path) as f:
        return json.load(f)


def test_output_csv_exists(workspace):
    """output.csv must exist."""
    assert (workspace / "output.csv").exists()


def test_aggregation_exists(workspace):
    """aggregation.json must exist."""
    assert (workspace / "aggregation.json").exists()


def test_notification_exists(workspace):
    """notification.json must exist."""
    assert (workspace / "notification.json").exists()


def test_output_only_completed_orders(output_csv):
    """Output should only contain completed orders (filter applied)."""
    for row in output_csv:
        assert row.get("status") == "completed", \
            f"Non-completed order found: {row.get('order_id')} status={row.get('status')}"


def test_output_row_count(output_csv):
    """Should have 24 completed orders."""
    assert len(output_csv) == 24, f"Expected 24 rows, got {len(output_csv)}"


def test_output_has_total_column(output_csv):
    """Output CSV must have a 'total' column from transform step."""
    assert "total" in output_csv[0], "Missing 'total' column in output"


def test_total_computed_correctly(output_csv):
    """The total column should equal quantity * price."""
    for row in output_csv:
        expected = float(row["quantity"]) * float(row["price"])
        actual = float(row["total"])
        assert abs(actual - expected) < 0.02, \
            f"Order {row['order_id']}: expected total {expected}, got {actual}"


def test_aggregation_has_groups(aggregation):
    """Aggregation must have groups."""
    groups = aggregation.get("groups", [])
    assert len(groups) == 3, f"Expected 3 category groups, got {len(groups)}"


def test_aggregation_categories(aggregation):
    """Aggregation must cover Electronics, Clothing, and Books."""
    groups = aggregation.get("groups", [])
    categories = {g.get("category") for g in groups}
    for cat in ["Electronics", "Clothing", "Books"]:
        assert cat in categories, f"Category '{cat}' missing from aggregation"


def test_aggregation_revenue_values(aggregation):
    """Aggregation revenue values must be approximately correct."""
    groups = aggregation.get("groups", [])
    expected = {"Electronics": 3889.76, "Clothing": 1114.84, "Books": 447.82}
    for g in groups:
        cat = g.get("category")
        if cat in expected:
            actual = g.get("total_revenue", 0)
            assert abs(actual - expected[cat]) < 5.0, \
                f"{cat} revenue: expected ~{expected[cat]}, got {actual}"


def test_notification_input_rows(notification):
    """Notification must report 30 input rows."""
    assert notification.get("input_rows") == 30


def test_notification_output_rows(notification):
    """Notification must report 24 output rows."""
    assert notification.get("output_rows") == 24


def test_notification_status(notification):
    """Notification status must be success."""
    assert notification.get("status") == "success"


def test_notification_has_summary(notification):
    """Notification must have a summary string."""
    summary = notification.get("summary", "")
    assert len(summary) > 10, "Summary is too short or missing"
