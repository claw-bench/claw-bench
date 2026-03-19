import os
from pathlib import Path
import json
import csv
import math
import pytest

@pytest.fixture
def workspace(request):
    """Resolve workspace from --workspace CLI option."""
    ws = request.config.getoption("--workspace")
    if ws:
        return Path(ws)
    return Path(os.environ.get("CLAW_WORKSPACE", os.environ.get("WORKSPACE", "workspace")))
@pytest.mark.weight(3)
def test_mc_results_csv_exists(workspace):
    csv_path = workspace / "mc_results.csv"
    assert csv_path.exists(), "mc_results.csv file does not exist"

@pytest.mark.weight(5)
def test_mc_results_csv_content(workspace):
    csv_path = workspace / "mc_results.csv"
    with csv_path.open(newline='') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    expected_ns = [100, 1000, 10000, 100000, 1000000]
    assert len(rows) == len(expected_ns), f"Expected {len(expected_ns)} rows, got {len(rows)}"

    prev_error = None
    prev_n = None
    for i, row in enumerate(rows):
        n = int(row['n'])
        estimate = float(row['estimate'])
        error = float(row['error'])
        conv_rate = row['convergence_rate']

        # Check sample size
        assert n == expected_ns[i], f"Row {i} sample size {n} does not match expected {expected_ns[i]}"

        # Estimate should be reasonable: pi approx 3.14
        assert 2.5 < estimate < 4.0, f"Estimate {estimate} out of expected range"

        # Error should be positive and less than 1
        assert 0 <= error < 1, f"Error {error} out of expected range"

        # Check convergence rate
        if i == 0:
            assert conv_rate.lower() == 'null', "First convergence_rate should be null"
        else:
            conv_val = float(conv_rate)
            # Convergence rate should be positive and typically near 0.5 for MC
            assert 0 < conv_val < 2, f"Convergence rate {conv_val} out of expected range"

        # Check error decreases as n increases (not strictly monotone but generally)
        if prev_error is not None:
            assert error <= prev_error * 1.5, "Error did not decrease reasonably with larger n"

        prev_error = error
        prev_n = n

@pytest.mark.weight(2)
def test_mc_summary_json_content(workspace):
    json_path = workspace / "mc_summary.json"
    assert json_path.exists(), "mc_summary.json file does not exist"

    with json_path.open() as f:
        data = json.load(f)

    # Check keys
    for key in ['true_pi', 'estimates', 'errors', 'convergence_rates']:
        assert key in data, f"Key '{key}' missing in mc_summary.json"

    true_pi = data['true_pi']
    assert abs(true_pi - math.pi) < 1e-10, "true_pi value incorrect"

    estimates = data['estimates']
    errors = data['errors']
    conv_rates = data['convergence_rates']

    expected_len = 5
    assert len(estimates) == expected_len
    assert len(errors) == expected_len
    assert len(conv_rates) == expected_len

    # Check types and values
    for i in range(expected_len):
        assert isinstance(estimates[i], float), "Estimates must be floats"
        assert isinstance(errors[i], float), "Errors must be floats"

    # First convergence rate is None/null
    assert conv_rates[0] is None

    for cr in conv_rates[1:]:
        assert isinstance(cr, float), "Convergence rates after first must be floats"
        assert 0 < cr < 2

@pytest.mark.weight(1)
def test_csv_formatting(workspace):
    csv_path = workspace / "mc_results.csv"
    with csv_path.open() as f:
        lines = f.readlines()

    # Check header
    assert lines[0].strip() == 'n,estimate,error,convergence_rate'

    # Check numeric formatting with at least 6 decimals for estimate and error
    for line in lines[1:]:
        parts = line.strip().split(',')
        assert len(parts) == 4
        # n is int
        int(parts[0])
        # estimate and error have at least 6 decimals
        est_decimals = parts[1].split('.')[-1]
        err_decimals = parts[2].split('.')[-1]
        assert len(est_decimals) >= 6, f"Estimate decimals less than 6 in line: {line.strip()}"
        assert len(err_decimals) >= 6, f"Error decimals less than 6 in line: {line.strip()}"

@pytest.mark.weight(1)
def test_json_values_consistency(workspace):
    # Check that values in JSON and CSV match
    import csv
    json_path = workspace / "mc_summary.json"
    csv_path = workspace / "mc_results.csv"

    with json_path.open() as f:
        data = json.load(f)

    with csv_path.open(newline='') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    for i, row in enumerate(rows):
        est_csv = float(row['estimate'])
        err_csv = float(row['error'])

        est_json = data['estimates'][i]
        err_json = data['errors'][i]

        assert abs(est_csv - est_json) < 1e-8
        assert abs(err_csv - err_json) < 1e-8

    # Convergence rates
    for i, row in enumerate(rows):
        conv_csv = row['convergence_rate']
        conv_json = data['convergence_rates'][i]
        if conv_csv.lower() == 'null':
            assert conv_json is None
        else:
            assert abs(float(conv_csv) - conv_json) < 1e-8
