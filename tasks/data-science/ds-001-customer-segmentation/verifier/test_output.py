import os
import pytest
import csv
import json
from pathlib import Path

@pytest.fixture
def workspace(tmp_path_factory):
    return Path(os.environ.get("CLAW_WORKSPACE", "/workspace"))

@pytest.mark.weight(3)
def test_segmentation_csv(workspace):
    path = workspace / "segmentation_results.csv"
    assert path.exists(), "segmentation_results.csv not found"
    with open(path) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    assert len(rows) == 100, f"Expected 100 rows, got {len(rows)}"
    # Check segment column exists
    has_segment = any("segment" in col.lower() or "cluster" in col.lower() or "label" in col.lower() for col in reader.fieldnames)
    assert has_segment, "No segment/cluster/label column found"

@pytest.mark.weight(3)
def test_analysis_json(workspace):
    path = workspace / "analysis.json"
    assert path.exists(), "analysis.json not found"
    data = json.loads(path.read_text())
    assert "optimal_k" in data
    assert data["optimal_k"] in [3, 4, 5]
    assert "inertia_values" in data

@pytest.mark.weight(2)
def test_segment_profiles(workspace):
    data = json.loads((workspace / "analysis.json").read_text())
    assert "segment_profiles" in data
    profiles = data["segment_profiles"]
    total = sum(p.get("size", p.get("count", 0)) for p in profiles.values())
    assert total == 100, f"Segment sizes should sum to 100, got {total}"

@pytest.mark.weight(2)
def test_segment_names(workspace):
    data = json.loads((workspace / "analysis.json").read_text())
    assert "segment_names" in data
    assert len(data["segment_names"]) == data["optimal_k"]

@pytest.mark.weight(2)
def test_report_exists(workspace):
    path = workspace / "report.md"
    assert path.exists(), "report.md not found"
    assert len(path.read_text()) > 100
