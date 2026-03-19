import json
import pytest
import numpy as np
import pandas as pd
from pathlib import Path

@pytest.fixture
def workspace_path():
    return Path("workspace")

def test_output_file_exists(workspace_path):
    output_file = workspace_path / "risk_report.json"
    assert output_file.exists(), "risk_report.json not found"

@pytest.mark.weight(3)
def test_output_format(workspace_path):
    output_file = workspace_path / "risk_report.json"
    with open(output_file) as f:
        data = json.load(f)
    
    assert "historical" in data, "Missing historical results"
    assert "parametric" in data, "Missing parametric results"
    assert "summary" in data, "Missing summary"
    
    for method in ["historical", "parametric"]:
        for metric in ["var_95", "var_99", "cvar_95", "cvar_99"]:
            assert metric in data[method], f"Missing {metric} in {method}"

@pytest.mark.weight(4)
def test_calculations_correct(workspace_path):
    # Load input data
    df = pd.read_csv(workspace_path / "portfolio_returns.csv")
    returns = df["daily_return"].values
    
    # Load output
    output_file = workspace_path / "risk_report.json"
    with open(output_file) as f:
        data = json.load(f)
    
    # Test historical VaR
    historical_var_95 = np.percentile(returns, 5)
    assert abs(data["historical"]["var_95"] - historical_var_95) < 1e-6, "Historical 95% VaR incorrect"
    
    # Test parametric VaR (using sample mean and std)
    mean, std = np.mean(returns), np.std(returns)
    from scipy.stats import norm
    parametric_var_95 = mean + std * norm.ppf(0.05)
    assert abs(data["parametric"]["var_95"] - parametric_var_95) < 1e-6, "Parametric 95% VaR incorrect"

@pytest.mark.weight(3)
def test_summary_correct(workspace_path):
    output_file = workspace_path / "risk_report.json"
    with open(output_file) as f:
        data = json.load(f)
    
    # Determine which method is actually more conservative
    hist_var = data["historical"]["var_95"]
    param_var = data["parametric"]["var_95"]
    actual_more_conservative = "historical" if hist_var < param_var else "parametric"
    
    assert actual_more_conservative in data["summary"].lower(), "Summary incorrectly identifies conservative method"

def test_no_hardcoding(workspace_path):
    output_file = workspace_path / "risk_report.json"
    with open(output_file) as f:
        data = json.load(f)
    
    # Check for obviously wrong values
    for method in ["historical", "parametric"]:
        for metric in data[method].values():
            assert isinstance(metric, float), "Values must be calculated, not hardcoded"
            assert -0.1 < metric < 0, "Risk metrics should be negative and reasonable in magnitude"
