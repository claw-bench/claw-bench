import os
import pytest
import json
import csv
from pathlib import Path

@pytest.fixture
def workspace(tmp_path_factory):
    return Path(os.environ.get("CLAW_WORKSPACE", "/workspace"))

@pytest.mark.weight(3)
def test_analysis_json(workspace):
    path = workspace / "citation_analysis.json"
    assert path.exists(), "citation_analysis.json not found"
    data = json.loads(path.read_text())
    assert data["total_papers"] == 20
    assert data["total_edges"] > 30

@pytest.mark.weight(3)
def test_top_cited(workspace):
    data = json.loads((workspace / "citation_analysis.json").read_text())
    assert "top_cited" in data
    top = data["top_cited"]
    assert len(top) >= 3
    # vaswani2017attention should be most cited
    top_ids = [t.get("id","") for t in top]
    assert "vaswani2017attention" in top_ids, "vaswani2017attention should be top cited"

@pytest.mark.weight(2)
def test_uncited(workspace):
    data = json.loads((workspace / "citation_analysis.json").read_text())
    assert "uncited_papers" in data

@pytest.mark.weight(2)
def test_network_csv(workspace):
    path = workspace / "network.csv"
    assert path.exists(), "network.csv not found"
    with open(path) as f:
        reader = csv.reader(f)
        rows = list(reader)
    assert len(rows) > 30, "Network should have 30+ edges"

@pytest.mark.weight(2)
def test_summary(workspace):
    path = workspace / "analysis_summary.md"
    assert path.exists(), "analysis_summary.md not found"
    assert len(path.read_text()) > 200
