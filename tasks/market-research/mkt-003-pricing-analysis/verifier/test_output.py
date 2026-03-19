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
def test_pricing_analysis_output(workspace):
    analysis_file = workspace / "pricing_analysis.json"
    assert analysis_file.exists(), "pricing_analysis.json file must exist"

    with open(analysis_file) as f:
        data = json.load(f)

    # Check keys
    for key in ["elasticities", "avg_elasticity", "optimal_price", "max_revenue_estimate"]:
        assert key in data, f"Missing key {key} in output JSON"

    elasticities = data["elasticities"]
    avg_elasticity = data["avg_elasticity"]
    optimal_price = data["optimal_price"]
    max_revenue = data["max_revenue_estimate"]

    # Check elasticities is a non-empty list of floats
    assert isinstance(elasticities, list) and len(elasticities) >= 20
    for e in elasticities:
        assert isinstance(e, (float, int))

    # avg_elasticity should be float and roughly average of elasticities
    computed_avg = sum(elasticities) / len(elasticities)
    assert abs(avg_elasticity - computed_avg) < 1e-3

    # optimal_price should be positive float
    assert isinstance(optimal_price, (float, int)) and optimal_price > 0

    # max_revenue should be positive float
    assert isinstance(max_revenue, (float, int)) and max_revenue > 0

    # Additional sanity: optimal_price should be near last price (within factor 0.5 to 1.5)
    import csv
    with open(workspace / "pricing_history.csv") as f:
        rows = list(csv.DictReader(f))
    last_price = float(rows[-1]["price"])
    assert 0.5 * last_price <= optimal_price <= 1.5 * last_price

    # max_revenue should be roughly >= last revenue
    last_revenue = float(rows[-1]["revenue"])
    assert max_revenue >= last_revenue * 0.8
