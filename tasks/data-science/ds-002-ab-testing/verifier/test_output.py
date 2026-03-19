import os
from pathlib import Path
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
def test_ab_results_exists(workspace):
    result_file = workspace / "ab_results.json"
    assert result_file.exists(), "Output file ab_results.json does not exist"

@pytest.mark.weight(5)
def test_ab_results_content(workspace):
    result_file = workspace / "ab_results.json"
    data = json.loads(result_file.read_text())

    # Check keys
    keys = ["control_rate", "treatment_rate", "lift", "chi2", "p_value", "significant", "recommendation"]
    for key in keys:
        assert key in data, f"Missing key {key} in output"

    control_rate = data["control_rate"]
    treatment_rate = data["treatment_rate"]
    lift = data["lift"]
    chi2 = data["chi2"]
    p_value = data["p_value"]
    significant = data["significant"]
    recommendation = data["recommendation"]

    # Validate types
    assert isinstance(control_rate, float), "control_rate must be float"
    assert isinstance(treatment_rate, float), "treatment_rate must be float"
    assert isinstance(lift, float), "lift must be float"
    assert isinstance(chi2, float), "chi2 must be float"
    assert isinstance(p_value, float), "p_value must be float"
    assert isinstance(significant, bool), "significant must be bool"
    assert isinstance(recommendation, str), "recommendation must be string"

    # Check conversion rates are between 0 and 1
    assert 0 <= control_rate <= 1, "control_rate out of range"
    assert 0 <= treatment_rate <= 1, "treatment_rate out of range"

    # Check lift calculation
    expected_lift = (treatment_rate - control_rate) / control_rate if control_rate > 0 else 0
    assert abs(lift - expected_lift) < 1e-6, "lift calculation incorrect"

    # Check recommendation logic
    if significant and lift > 0:
        assert recommendation == "Implement treatment", "Recommendation incorrect when significant and lift > 0"
    else:
        assert recommendation == "Do not implement treatment", "Recommendation incorrect when not significant or lift <= 0"

@pytest.mark.weight(2)
def test_chi2_pvalue(workspace):
    import math
    from scipy.stats import chi2 as chi2_dist

    result_file = workspace / "ab_results.json"
    data = json.loads(result_file.read_text())

    chi2 = data["chi2"]
    p_value = data["p_value"]

    # p_value should be consistent with chi2 statistic and df=1
    p_calc = 1 - chi2_dist.cdf(chi2, df=1)
    assert abs(p_value - p_calc) < 1e-4, "p_value inconsistent with chi2 statistic"
