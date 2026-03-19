import os, pytest, json
from pathlib import Path

@pytest.fixture
def workspace(request):
    """Resolve workspace from --workspace CLI option."""
    ws = request.config.getoption("--workspace")
    if ws:
        return Path(ws)
    return Path(os.environ.get("CLAW_WORKSPACE", os.environ.get("WORKSPACE", "workspace")))
@pytest.fixture
def result(workspace):
    path = workspace / "risk_report.json"
    assert path.exists(), "risk_report.json not found"
    return json.loads(path.read_text())

@pytest.mark.weight(2)
def test_basic_stats(result):
    for k in ["mean_daily_return", "daily_std", "annualized_return", "annualized_volatility"]:
        assert k in result
        assert isinstance(result[k], (int, float))

@pytest.mark.weight(3)
def test_var(result):
    assert "var_95" in result and "var_99" in result
    assert result["var_95"] < 0
    assert result["var_99"] < result["var_95"]

@pytest.mark.weight(3)
def test_sharpe(result):
    assert "sharpe_ratio" in result
    assert isinstance(result["sharpe_ratio"], (int, float))

@pytest.mark.weight(2)
def test_max_drawdown(result):
    assert "max_drawdown" in result
    assert result["max_drawdown"] <= 0

@pytest.mark.weight(2)
def test_risk_rating(result):
    assert result.get("risk_rating") in ["poor", "moderate", "good", "excellent"]
