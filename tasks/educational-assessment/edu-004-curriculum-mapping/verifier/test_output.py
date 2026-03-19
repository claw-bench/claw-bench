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
def test_alignment_matrix(workspace):
    path = workspace / "alignment_matrix.csv"
    assert path.exists()
    with open(path) as f:
        rows = list(csv.DictReader(f))
    assert len(rows) >= 15

@pytest.mark.weight(3)
def test_gap_analysis(workspace):
    data = json.loads((workspace / "gap_analysis.json").read_text())
    assert data["total_objectives"] == 20
    assert data["total_standards"] == 15
    assert 0 <= data["coverage_rate"] <= 1

@pytest.mark.weight(2)
def test_unmapped(workspace):
    data = json.loads((workspace / "gap_analysis.json").read_text())
    assert isinstance(data["unmapped_objectives"], list)
    assert isinstance(data["uncovered_standards"], list)

@pytest.mark.weight(2)
def test_alignment_summary(workspace):
    data = json.loads((workspace / "gap_analysis.json").read_text())
    assert "alignment_summary" in data
    assert len(data["alignment_summary"]) == 20
