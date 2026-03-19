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
    path = workspace / "arbitrage_results.json"
    assert path.exists()
    return json.loads(path.read_text())

@pytest.mark.weight(3)
def test_opportunities_structure(result):
    assert "opportunities" in result
    assert isinstance(result["opportunities"], list)
    for opp in result["opportunities"]:
        assert "path" in opp
        assert "profit_pct" in opp
        assert len(opp["path"]) == 4
        assert opp["path"][0] == opp["path"][-1]

@pytest.mark.weight(3)
def test_profit_positive(result):
    for opp in result["opportunities"]:
        assert opp["profit_pct"] > 0

@pytest.mark.weight(2)
def test_total_count(result):
    assert result["total_opportunities"] == len(result["opportunities"])

@pytest.mark.weight(2)
def test_best_opportunity(result):
    if result["opportunities"]:
        assert "best_opportunity" in result
        best = result["best_opportunity"]
        max_profit = max(o["profit_pct"] for o in result["opportunities"])
        assert abs(best["profit_pct"] - max_profit) < 0.01
