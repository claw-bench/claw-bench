"""Verifier for data-010: Multi-Source Merge and Trend Analysis."""

from pathlib import Path
import csv
import json
import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def merged_rows(workspace):
    path = workspace / "merged.csv"
    assert path.exists(), "merged.csv not found"
    with open(path) as f:
        return list(csv.DictReader(f))


@pytest.fixture
def trends(workspace):
    path = workspace / "trends.json"
    assert path.exists(), "trends.json not found"
    return json.loads(path.read_text())


def test_merged_file_exists(workspace):
    assert (workspace / "merged.csv").exists()


def test_trends_file_exists(workspace):
    assert (workspace / "trends.json").exists()


def test_correct_total_rows(merged_rows):
    assert len(merged_rows) == 48, f"Expected 48 merged rows, got {len(merged_rows)}"


def test_all_quarters_represented(merged_rows):
    quarters = set(r["quarter"] for r in merged_rows)
    assert quarters == {"Q1", "Q2", "Q3"}, f"Expected Q1, Q2, Q3; got {quarters}"


def test_quarter_column_present(workspace):
    path = workspace / "merged.csv"
    header = path.read_text().strip().splitlines()[0]
    assert "quarter" in header


def test_growth_rates_reasonable(trends):
    for t in trends:
        assert -100 < t["q1_to_q2_growth"] < 200, f"Unreasonable Q1->Q2 growth for {t['product']}"
        assert -100 < t["q2_to_q3_growth"] < 200, f"Unreasonable Q2->Q3 growth for {t['product']}"


def test_growth_rates_correct(trends):
    expected = [{"product": "Doohickey", "q1_to_q2_growth": 7.14, "q2_to_q3_growth": 4.34}, {"product": "Gadget", "q1_to_q2_growth": 10.14, "q2_to_q3_growth": 8.8}, {"product": "Thingamajig", "q1_to_q2_growth": 3.73, "q2_to_q3_growth": 4.72}, {"product": "Widget", "q1_to_q2_growth": 21.83, "q2_to_q3_growth": 16.03}]
    trends_by_prod = {t["product"]: t for t in trends}
    for exp in expected:
        prod = exp["product"]
        assert prod in trends_by_prod, f"Missing product {prod} in trends"
        actual = trends_by_prod[prod]
        assert abs(actual["q1_to_q2_growth"] - exp["q1_to_q2_growth"]) < 0.1, \
            f"{prod} Q1->Q2: expected {exp['q1_to_q2_growth']}, got {actual['q1_to_q2_growth']}"
        assert abs(actual["q2_to_q3_growth"] - exp["q2_to_q3_growth"]) < 0.1, \
            f"{prod} Q2->Q3: expected {exp['q2_to_q3_growth']}, got {actual['q2_to_q3_growth']}"


def test_trends_sorted_by_product(trends):
    prods = [t["product"] for t in trends]
    assert prods == sorted(prods), "Trends not sorted by product name"
