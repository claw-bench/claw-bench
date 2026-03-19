import os
from pathlib import Path
import json
import pytest
import csv

@pytest.fixture
def workspace(request):
    """Resolve workspace from --workspace CLI option."""
    ws = request.config.getoption("--workspace")
    if ws:
        return Path(ws)
    return Path(os.environ.get("CLAW_WORKSPACE", os.environ.get("WORKSPACE", "workspace")))
@pytest.mark.weight(3)
def test_nps_report_exists(workspace):
    report_path = workspace / "nps_report.json"
    assert report_path.exists(), "nps_report.json file does not exist"

@pytest.mark.weight(5)
def test_nps_report_structure(workspace):
    report_path = workspace / "nps_report.json"
    with open(report_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Check keys
    expected_keys = {"overall_nps", "segment_nps", "total_responses", "promoter_pct", "detractor_pct", "passive_pct"}
    assert expected_keys == set(data.keys()), f"JSON keys mismatch. Expected {expected_keys}, got {set(data.keys())}"

    # Check types
    assert isinstance(data["overall_nps"], float), "overall_nps should be float"
    assert isinstance(data["segment_nps"], dict), "segment_nps should be a dict"
    assert isinstance(data["total_responses"], int), "total_responses should be int"
    assert isinstance(data["promoter_pct"], float), "promoter_pct should be float"
    assert isinstance(data["detractor_pct"], float), "detractor_pct should be float"
    assert isinstance(data["passive_pct"], float), "passive_pct should be float"

@pytest.mark.weight(7)
def test_nps_report_values(workspace):
    csv_path = workspace / "survey_responses.csv"
    report_path = workspace / "nps_report.json"

    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = list(csv.DictReader(f))

    with open(report_path, "r", encoding="utf-8") as f:
        report = json.load(f)

    total_responses = len(reader)
    assert report["total_responses"] == total_responses, f"total_responses mismatch: expected {total_responses}, got {report['total_responses']}"

    # Calculate overall counts
    promoters = sum(1 for r in reader if int(r["recommend_0_10"]) >= 9)
    detractors = sum(1 for r in reader if int(r["recommend_0_10"]) <= 6)
    passives = total_responses - promoters - detractors

    promoter_pct = round(promoters / total_responses * 100, 2)
    detractor_pct = round(detractors / total_responses * 100, 2)
    passive_pct = round(passives / total_responses * 100, 2)

    # Check percentages
    assert abs(report["promoter_pct"] - promoter_pct) < 0.01, f"promoter_pct mismatch: expected {promoter_pct}, got {report['promoter_pct']}"
    assert abs(report["detractor_pct"] - detractor_pct) < 0.01, f"detractor_pct mismatch: expected {detractor_pct}, got {report['detractor_pct']}"
    assert abs(report["passive_pct"] - passive_pct) < 0.01, f"passive_pct mismatch: expected {passive_pct}, got {report['passive_pct']}"

    # Check overall NPS
    expected_overall_nps = round(promoter_pct - detractor_pct, 2)
    assert abs(report["overall_nps"] - expected_overall_nps) < 0.01, f"overall_nps mismatch: expected {expected_overall_nps}, got {report['overall_nps']}"

    # Check segment NPS
    age_groups = set(r["age_group"] for r in reader)
    segment_nps = report["segment_nps"]
    assert set(segment_nps.keys()) == age_groups, f"segment_nps keys mismatch: expected {age_groups}, got {set(segment_nps.keys())}"

    for group in age_groups:
        group_rows = [r for r in reader if r["age_group"] == group]
        if not group_rows:
            continue
        group_total = len(group_rows)
        group_promoters = sum(1 for r in group_rows if int(r["recommend_0_10"]) >= 9)
        group_detractors = sum(1 for r in group_rows if int(r["recommend_0_10"]) <= 6)
        group_promoter_pct = group_promoters / group_total * 100
        group_detractor_pct = group_detractors / group_total * 100
        expected_segment_nps = round(group_promoter_pct - group_detractor_pct, 2)
        assert abs(segment_nps[group] - expected_segment_nps) < 0.01, f"segment_nps for {group} mismatch: expected {expected_segment_nps}, got {segment_nps[group]}"
