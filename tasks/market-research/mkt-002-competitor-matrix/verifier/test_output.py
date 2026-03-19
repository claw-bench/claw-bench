import os
from pathlib import Path
import csv
import json
import pytest

@pytest.fixture
def workspace(request):
    """Resolve workspace from --workspace CLI option."""
    ws = request.config.getoption("--workspace")
    if ws:
        return Path(ws)
    return Path(os.environ.get("CLAW_WORKSPACE", os.environ.get("WORKSPACE", "workspace")))
@pytest.mark.weight(3)
def test_competitor_matrix_file_exists(workspace):
    matrix_file = workspace / "competitor_matrix.csv"
    assert matrix_file.exists(), "competitor_matrix.csv file does not exist"

@pytest.mark.weight(5)
def test_competitor_matrix_content(workspace):
    matrix_file = workspace / "competitor_matrix.csv"
    with matrix_file.open() as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Check at least one row per company
    companies = set(row["company"] for row in rows)
    assert len(companies) >= 5, "Expected at least 5 companies in competitor_matrix.csv"

    # Check columns and score ranges
    for row in rows:
        for col in ["price_competitiveness", "feature_richness", "customer_satisfaction", "market_position"]:
            val = float(row[col])
            assert 1.0 <= val <= 10.0, f"Score {col} out of range: {val}"

@pytest.mark.weight(4)
def test_competitive_summary_json(workspace):
    summary_file = workspace / "competitive_summary.json"
    assert summary_file.exists(), "competitive_summary.json file does not exist"

    with summary_file.open() as f:
        data = json.load(f)

    expected_keys = {"price_competitiveness", "feature_richness", "customer_satisfaction", "market_position"}
    assert set(data.keys()) == expected_keys, "JSON keys mismatch"

    # Each value should be a list of companies
    for criterion, companies in data.items():
        assert isinstance(companies, list), f"Value for {criterion} is not a list"
        assert len(companies) >= 5, f"Expected at least 5 companies in {criterion} ranking"

@pytest.mark.weight(3)
def test_ranking_order(workspace):
    # Check that companies are ordered descending by score in JSON summary
    matrix_file = workspace / "competitor_matrix.csv"
    summary_file = workspace / "competitive_summary.json"

    with matrix_file.open() as f:
        reader = csv.DictReader(f)
        scores = {}
        for row in reader:
            company = row["company"]
            scores[company] = {
                "price_competitiveness": float(row["price_competitiveness"]),
                "feature_richness": float(row["feature_richness"]),
                "customer_satisfaction": float(row["customer_satisfaction"]),
                "market_position": float(row["market_position"]),
            }

    with summary_file.open() as f:
        summary = json.load(f)

    for criterion, ranked_companies in summary.items():
        # Check descending order
        prev_score = None
        for company in ranked_companies:
            score = scores.get(company, {}).get(criterion, None)
            assert score is not None, f"Company {company} missing score for {criterion}"
            if prev_score is not None:
                assert score <= prev_score + 1e-6, f"Ranking order incorrect for {criterion}"
            prev_score = score
