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
def test_incident_report_exists(workspace):
    report_path = workspace / "incident_report.json"
    assert report_path.exists(), "incident_report.json file does not exist"

@pytest.mark.weight(5)
def test_incident_report_structure(workspace):
    report_path = workspace / "incident_report.json"
    with open(report_path, 'r') as f:
        data = json.load(f)

    # Check keys
    assert 'timeline' in data, "Missing 'timeline' key"
    assert 'anomalies' in data, "Missing 'anomalies' key"
    assert 'affected_services' in data, "Missing 'affected_services' key"
    assert 'severity' in data, "Missing 'severity' key"

    # timeline should be a list
    assert isinstance(data['timeline'], list), "'timeline' should be a list"
    # anomalies should be a list
    assert isinstance(data['anomalies'], list), "'anomalies' should be a list"
    # affected_services should be a list
    assert isinstance(data['affected_services'], list), "'affected_services' should be a list"
    # severity should be a string
    assert isinstance(data['severity'], str), "'severity' should be a string"

@pytest.mark.weight(7)
def test_detected_anomalies(workspace):
    report_path = workspace / "incident_report.json"
    with open(report_path, 'r') as f:
        data = json.load(f)

    anomalies = set(data['anomalies'])
    affected_services = set(data['affected_services'])
    severity = data['severity']

    # We expect all three anomaly types due to setup
    assert 'error_spikes' in anomalies, "Expected 'error_spikes' anomaly"
    assert 'repeated_patterns' in anomalies, "Expected 'repeated_patterns' anomaly"
    assert 'service_failures' in anomalies, "Expected 'service_failures' anomaly"

    # Check affected services include 'database' (failure), 'api' (repeated), and others from spikes
    assert 'database' in affected_services, "Expected 'database' in affected_services"
    assert 'api' in affected_services, "Expected 'api' in affected_services"

    # Severity should be 'high' due to multiple anomaly types
    assert severity == 'high', f"Expected severity 'high', got '{severity}'"

@pytest.mark.weight(5)
def test_timeline_entries(workspace):
    report_path = workspace / "incident_report.json"
    with open(report_path, 'r') as f:
        data = json.load(f)

    timeline = data['timeline']

    # Check timeline contains entries for error spikes, repeated patterns, and service failures
    types_found = set()
    for entry in timeline:
        desc = entry.get('description', '').lower()
        if 'error spike' in desc:
            types_found.add('error_spikes')
        if 'repeated' in desc:
            types_found.add('repeated_patterns')
        if 'service failure' in desc or 'failure' in desc:
            types_found.add('service_failures')

    assert 'error_spikes' in types_found, "Timeline missing error spike entries"
    assert 'repeated_patterns' in types_found, "Timeline missing repeated pattern entries"
    assert 'service_failures' in types_found, "Timeline missing service failure entries"
