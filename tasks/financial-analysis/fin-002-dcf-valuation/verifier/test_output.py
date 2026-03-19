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
    path = workspace / "dcf_valuation.json"
    assert path.exists(), "dcf_valuation.json not found"
    return json.loads(path.read_text())

@pytest.mark.weight(3)
def test_projected_fcf(result):
    assert "projected_fcf" in result
    fcf = result["projected_fcf"]
    assert len(fcf) == 5
    for v in fcf:
        assert isinstance(v, (int, float))
        assert v > 0

@pytest.mark.weight(3)
def test_wacc(result):
    assert "wacc" in result
    w = result["wacc"]
    assert 0.01 < w < 0.30

@pytest.mark.weight(3)
def test_terminal_value(result):
    assert "terminal_value" in result
    assert result["terminal_value"] > 0

@pytest.mark.weight(3)
def test_enterprise_and_equity(result):
    assert "enterprise_value" in result
    assert "equity_value" in result
    assert result["enterprise_value"] > 0
    assert result["equity_value"] > 0

@pytest.mark.weight(3)
def test_intrinsic_value(result):
    assert "intrinsic_value_per_share" in result
    assert result["intrinsic_value_per_share"] > 0

@pytest.mark.weight(2)
def test_valuation_summary(result):
    assert result.get("valuation_summary") in ["undervalued", "overvalued", "fairly_valued"]
