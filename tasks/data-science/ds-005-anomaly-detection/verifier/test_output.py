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
def test_anomalies_file_exists(workspace):
    anomalies_file = workspace / "anomalies.json"
    assert anomalies_file.exists(), "Output file anomalies.json does not exist"

@pytest.mark.weight(5)
def test_anomalies_structure(workspace):
    anomalies_file = workspace / "anomalies.json"
    data = json.loads(anomalies_file.read_text())
    assert isinstance(data, dict), "Output JSON should be a dictionary"
    # Check at least one sensor
    assert len(data) >= 1, "Output JSON should have at least one sensor"
    for sensor_id, info in data.items():
        assert 'iqr_anomalies' in info, f"Missing iqr_anomalies for {sensor_id}"
        assert 'zscore_anomalies' in info, f"Missing zscore_anomalies for {sensor_id}"
        assert 'anomaly_rate' in info, f"Missing anomaly_rate for {sensor_id}"
        assert isinstance(info['iqr_anomalies'], list), "iqr_anomalies should be a list"
        assert isinstance(info['zscore_anomalies'], list), "zscore_anomalies should be a list"
        ar = info['anomaly_rate']
        assert 'iqr' in ar and 'zscore' in ar, "anomaly_rate should have keys 'iqr' and 'zscore'"
        assert 0 <= ar['iqr'] <= 1, "iqr anomaly_rate should be between 0 and 1"
        assert 0 <= ar['zscore'] <= 1, "zscore anomaly_rate should be between 0 and 1"

@pytest.mark.weight(7)
def test_anomalies_consistency(workspace):
    import csv
    anomalies_file = workspace / "anomalies.json"
    data = json.loads(anomalies_file.read_text())

    # Load original data
    sensor_data = {}
    with open(workspace / "sensor_data.csv") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sensor_data.setdefault(row['sensor_id'], []).append({'timestamp': row['timestamp'], 'value': float(row['value'])})

    for sensor_id, info in data.items():
        original = sensor_data.get(sensor_id, [])
        total = len(original)
        # Check anomaly counts consistent with anomaly_rate
        iqr_count = len(info['iqr_anomalies'])
        zscore_count = len(info['zscore_anomalies'])
        iqr_rate = info['anomaly_rate']['iqr']
        zscore_rate = info['anomaly_rate']['zscore']
        assert abs(iqr_rate - iqr_count / total) < 1e-3, f"iqr anomaly_rate mismatch for {sensor_id}"
        assert abs(zscore_rate - zscore_count / total) < 1e-3, f"zscore anomaly_rate mismatch for {sensor_id}"

        # Check anomalies values and timestamps appear in original data
        orig_set = {(d['timestamp'], d['value']) for d in original}
        for anomaly in info['iqr_anomalies']:
            assert (anomaly['timestamp'], anomaly['value']) in orig_set, f"iqr anomaly not in original data for {sensor_id}"
        for anomaly in info['zscore_anomalies']:
            assert (anomaly['timestamp'], anomaly['value']) in orig_set, f"zscore anomaly not in original data for {sensor_id}"
