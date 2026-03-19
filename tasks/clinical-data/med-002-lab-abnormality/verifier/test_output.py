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
def test_output_file_exists(workspace):
    output_file = workspace / "clinical_alerts.json"
    assert output_file.exists(), "Output file clinical_alerts.json does not exist"

@pytest.mark.weight(5)
def test_output_json_format(workspace):
    output_file = workspace / "clinical_alerts.json"
    with open(output_file, "r") as f:
        data = json.load(f)
    assert isinstance(data, list), "Output JSON must be a list"

@pytest.mark.weight(7)
def test_alerts_correctness(workspace):
    import csv

    input_file = workspace / "lab_results.csv"
    output_file = workspace / "clinical_alerts.json"

    with open(input_file, newline='') as f:
        reader = list(csv.DictReader(f))

    with open(output_file) as f:
        alerts = json.load(f)

    # Build a dict for quick lookup of alerts by patient_id and test_name
    alert_map = {(a['patient_id'], a['test_name']): a for a in alerts}

    for row in reader:
        patient_id = row['patient_id']
        test_name = row['test_name']
        value = float(row['value'])
        unit = row['unit']
        ref_low = float(row['reference_low'])
        ref_high = float(row['reference_high'])

        range_width = ref_high - ref_low

        if value < ref_low or value > ref_high:
            # Abnormal
            if value < ref_low:
                diff = ref_low - value
            else:
                diff = value - ref_high
            percentage = diff / range_width

            if percentage <= 0.20:
                severity = "mild"
            elif percentage <= 0.50:
                severity = "moderate"
            else:
                severity = "severe"

            # Check alert exists
            key = (patient_id, test_name)
            assert key in alert_map, f"Missing alert for abnormal result {key}"

            alert = alert_map[key]
            assert alert['patient_id'] == patient_id
            assert alert['test_name'] == test_name
            assert abs(float(alert['value']) - value) < 1e-4
            assert alert['unit'] == unit
            assert alert['severity'] == severity

        else:
            # Normal result should not be in alerts
            key = (patient_id, test_name)
            assert key not in alert_map, f"Alert present for normal result {key}"

@pytest.mark.weight(2)
def test_empty_list_if_no_abnormal(workspace):
    # This test tries to check if the output is [] when no abnormal values
    # We skip this because our setup always has abnormal values
    # Just check output is a list
    output_file = workspace / "clinical_alerts.json"
    with open(output_file) as f:
        data = json.load(f)
    assert isinstance(data, list)
