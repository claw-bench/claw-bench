import os
import pytest
import json
from pathlib import Path

@pytest.fixture
def workspace(tmp_path_factory):
    return Path(os.environ.get("CLAW_WORKSPACE", "/workspace"))

@pytest.fixture
def result(workspace):
    path = workspace / "portfolio_analysis.json"
    assert path.exists(), "portfolio_analysis.json not found"
    return json.loads(path.read_text())

@pytest.mark.weight(3)
def test_has_individual_betas(result):
    assert "individual_betas" in result
    betas = result["individual_betas"]
    assert len(betas) == 5, f"Expected 5 stocks, got {len(betas)}"
    for stock in ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]:
        assert stock in betas, f"Missing beta for {stock}"
        assert isinstance(betas[stock], (int, float)), f"Beta for {stock} is not numeric"

@pytest.mark.weight(3)
def test_betas_reasonable(result):
    for stock, beta in result["individual_betas"].items():
        assert -1 < beta < 4, f"Beta for {stock} = {beta} is unreasonable"

@pytest.mark.weight(3)
def test_portfolio_beta(result):
    assert "portfolio_beta" in result
    pb = result["portfolio_beta"]
    assert isinstance(pb, (int, float))
    # Equal-weighted average of individual betas
    ind = list(result["individual_betas"].values())
    expected = sum(ind) / len(ind)
    assert abs(pb - expected) < 0.05, f"Portfolio beta {pb} != avg {expected}"

@pytest.mark.weight(2)
def test_risk_level(result):
    assert "portfolio_risk_level" in result
    pb = result["portfolio_beta"]
    if pb < 0.8:
        assert result["portfolio_risk_level"] == "conservative"
    elif pb <= 1.2:
        assert result["portfolio_risk_level"] == "moderate"
    else:
        assert result["portfolio_risk_level"] == "aggressive"

@pytest.mark.weight(1)
def test_json_valid(workspace):
    path = workspace / "portfolio_analysis.json"
    json.loads(path.read_text())
