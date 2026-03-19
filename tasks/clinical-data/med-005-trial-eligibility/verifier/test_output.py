import json
import os
from pathlib import Path
import pytest

@pytest.fixture
def workspace(request):
    """Resolve workspace from --workspace CLI option."""
    ws = request.config.getoption("--workspace")
    if ws:
        return Path(ws)
    return Path(os.environ.get("CLAW_WORKSPACE", os.environ.get("WORKSPACE", "workspace")))
@pytest.mark.weight(3)
def test_screening_report_exists(workspace):
    report_path = workspace / "screening_report.json"
    assert report_path.exists(), "screening_report.json file must be created"

@pytest.mark.weight(5)
def test_screening_report_structure(workspace):
    report_path = workspace / "screening_report.json"
    data = json.loads(report_path.read_text())
    assert isinstance(data, list), "Report must be a list"
    for entry in data:
        assert 'patient_id' in entry
        assert 'eligible' in entry
        assert 'reasons' in entry
        assert isinstance(entry['patient_id'], str)
        assert isinstance(entry['eligible'], bool)
        assert isinstance(entry['reasons'], list)

@pytest.mark.weight(7)
def test_eligibility_logic(workspace):
    import csv
    # Load criteria
    criteria_path = workspace / "trial_criteria.json"
    criteria = json.loads(criteria_path.read_text())
    inclusion = criteria.get('inclusion', {})
    exclusion = criteria.get('exclusion', {})

    # Load patients
    patients_path = workspace / "patients.csv"
    patients = []
    with open(patients_path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row['age'] = int(row['age'])
            row['lab_values'] = json.loads(row['lab_values_json'])
            patients.append(row)

    # Load report
    report_path = workspace / "screening_report.json"
    report = json.loads(report_path.read_text())
    report_map = {r['patient_id']: r for r in report}

    def check_criteria(patient):
        reasons = []
        # Inclusion checks
        inc_age = inclusion.get('age', {})
        if inc_age:
            if 'min' in inc_age and patient['age'] < inc_age['min']:
                reasons.append(f"Age {patient['age']} below minimum {inc_age['min']}")
            if 'max' in inc_age and patient['age'] > inc_age['max']:
                reasons.append(f"Age {patient['age']} above maximum {inc_age['max']}")

        inc_gender = inclusion.get('gender')
        if inc_gender and patient['gender'] not in inc_gender:
            reasons.append(f"Gender {patient['gender']} not in inclusion list")

        inc_diag = inclusion.get('diagnosis')
        if inc_diag and patient['diagnosis'] not in inc_diag:
            reasons.append(f"Diagnosis {patient['diagnosis']} not in inclusion list")

        inc_lab = inclusion.get('lab_values', {})
        for lab, bounds in inc_lab.items():
            val = patient['lab_values'].get(lab)
            if val is None:
                reasons.append(f"Lab value {lab} missing")
            else:
                if 'min' in bounds and val < bounds['min']:
                    reasons.append(f"Lab {lab} value {val} below minimum {bounds['min']}")
                if 'max' in bounds and val > bounds['max']:
                    reasons.append(f"Lab {lab} value {val} above maximum {bounds['max']}")

        # Exclusion checks
        exc_diag = exclusion.get('diagnosis', [])
        if patient['diagnosis'] in exc_diag:
            reasons.append(f"Diagnosis {patient['diagnosis']} in exclusion list")

        exc_lab = exclusion.get('lab_values', {})
        for lab, bounds in exc_lab.items():
            val = patient['lab_values'].get(lab)
            if val is not None:
                # If max specified, value above max excludes
                if 'max' in bounds and val > bounds['max']:
                    reasons.append(f"Lab {lab} value {val} above exclusion max {bounds['max']}")
                # If min specified, value below min excludes
                if 'min' in bounds and val < bounds['min']:
                    reasons.append(f"Lab {lab} value {val} below exclusion min {bounds['min']}")

        return reasons

    for patient in patients:
        pid = patient['patient_id']
        assert pid in report_map, f"Patient {pid} missing in report"
        entry = report_map[pid]
        expected_reasons = check_criteria(patient)
        expected_eligible = len(expected_reasons) == 0

        # Check eligibility matches
        assert entry['eligible'] == expected_eligible, (
            f"Eligibility mismatch for patient {pid}: expected {expected_eligible}, got {entry['eligible']}")

        # Check reasons match (order may differ)
        assert sorted(entry['reasons']) == sorted(expected_reasons), (
            f"Reasons mismatch for patient {pid}: expected {expected_reasons}, got {entry['reasons']}")
