import os, pytest, json, csv
from pathlib import Path

@pytest.fixture
def workspace(request):
    """Resolve workspace from --workspace CLI option."""
    ws = request.config.getoption("--workspace")
    if ws:
        return Path(ws)
    return Path(os.environ.get("CLAW_WORKSPACE", os.environ.get("WORKSPACE", "workspace")))
@pytest.mark.weight(3)
def test_comparison_csv(workspace):
    path = workspace / "earnings_comparison.csv"
    assert path.exists()
    with open(path) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    assert len(rows) >= 5
    headers = rows[0].keys()
    for h in ["metric", "q1_value", "q2_value"]:
        assert h in headers

@pytest.mark.weight(3)
def test_summary_json(workspace):
    path = workspace / "earnings_summary.json"
    assert path.exists()
    data = json.loads(path.read_text())
    assert "q1" in data and "q2" in data
    for q in ["q1", "q2"]:
        assert "revenue" in data[q]
        assert "net_income" in data[q]

@pytest.mark.weight(2)
def test_trend(workspace):
    data = json.loads((workspace / "earnings_summary.json").read_text())
    assert data.get("trend") in ["improving", "declining", "mixed"]

@pytest.mark.weight(2)
def test_values_numeric(workspace):
    data = json.loads((workspace / "earnings_summary.json").read_text())
    for q in ["q1", "q2"]:
        for k, v in data[q].items():
            assert isinstance(v, (int, float))
