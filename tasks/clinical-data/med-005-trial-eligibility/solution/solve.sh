#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

python3 - <<EOF
import os; WORKSPACE = os.environ.get('WORKSPACE', os.getcwd())
import csv
import json

# Load patients
patients = []
with open(f'{WORKSPACE}/patients.csv', newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        row['age'] = int(row['age'])
        row['lab_values'] = json.loads(row['lab_values_json'])
        patients.append(row)

# Load criteria
with open(f'{WORKSPACE}/trial_criteria.json') as f:
    criteria = json.load(f)

inclusion = criteria.get('inclusion', {})
exclusion = criteria.get('exclusion', {})

results = []

for patient in patients:
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
            if 'max' in bounds and val > bounds['max']:
                reasons.append(f"Lab {lab} value {val} above exclusion max {bounds['max']}")
            if 'min' in bounds and val < bounds['min']:
                reasons.append(f"Lab {lab} value {val} below exclusion min {bounds['min']}")

    eligible = len(reasons) == 0
    results.append({
        'patient_id': patient['patient_id'],
        'eligible': eligible,
        'reasons': reasons
    })

with open(f'{WORKSPACE}/screening_report.json', 'w') as f:
    json.dump(results, f, indent=2)
EOF
