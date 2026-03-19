import json
import pytest
import pandas as pd
from pathlib import Path

@pytest.fixture
def workspace_path():
    return Path(__file__).parent.parent

@pytest.mark.weight(3)
def test_output_file_exists(workspace_path):
    output_file = workspace_path / "wacc_report.json"
    assert output_file.exists(), "Output file not found"

@pytest.mark.weight(4)
def test_output_format(workspace_path):
    output_file = workspace_path / "wacc_report.json"
    with open(output_file) as f:
        data = json.load(f)
    
    required_keys = {
        "equity_weight", "debt_weight", 
        "cost_of_equity", "cost_of_debt",
        "tax_rate", "final_wacc"
    }
    assert set(data.keys()) == required_keys, "Missing required keys in output"

@pytest.mark.weight(5)
def test_calculations_correctness(workspace_path):
    output_file = workspace_path / "wacc_report.json"
    with open(output_file) as f:
        data = json.load(f)
    
    # Expected values based on synthetic data
    expected_equity_weight = 0.6  # 6000/(6000+4000)
    expected_debt_weight = 0.4    # 4000/(6000+4000)
    expected_cost_equity = 0.09   # 0.03 + 1.2*(0.08-0.03)
    expected_cost_debt = 0.05     # 200/4000
    expected_tax_rate = 0.2174    # 500/2300
    
    # Calculate expected WACC
    expected_wacc = (expected_equity_weight * expected_cost_equity + 
                    expected_debt_weight * expected_cost_debt * (1 - expected_tax_rate))
    
    assert abs(data["equity_weight"] - expected_equity_weight) < 0.001
    assert abs(data["debt_weight"] - expected_debt_weight) < 0.001
    assert abs(data["cost_of_equity"] - expected_cost_equity) < 0.001
    assert abs(data["cost_of_debt"] - expected_cost_debt) < 0.001
    assert abs(data["tax_rate"] - expected_tax_rate) < 0.001
    assert abs(data["final_wacc"] - expected_wacc) < 0.001

@pytest.mark.weight(3)
def test_edge_case_zero_debt(workspace_path):
    # Agent should handle zero debt scenario gracefully
    # This test would be run separately with edge case files
    pass

@pytest.mark.weight(3)
def test_edge_case_negative_equity(workspace_path):
    # Agent should handle negative equity scenario gracefully
    # This test would be run separately with edge case files
    pass

@pytest.mark.weight(2)
def test_rounding_applied(workspace_path):
    output_file = workspace_path / "wacc_report.json"
    with open(output_file) as f:
        data = json.load(f)
    
    for value in data.values():
        assert len(str(value).split('.')[1]) <= 4, "Values should be rounded to 4 decimal places"
