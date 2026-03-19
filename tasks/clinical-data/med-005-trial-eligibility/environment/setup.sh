#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

mkdir -p "$WORKSPACE"

# Generate patients.csv with 30 patients
python3 - <<EOF
import os; WORKSPACE = os.environ.get('WORKSPACE', os.getcwd())
import csv
import json
import random
random.seed(42)

patients = []
genders = ['M', 'F']
diagnoses = ['diabetes', 'hypertension', 'asthma', 'healthy', 'cancer']

lab_tests = ['HbA1c', 'Cholesterol', 'BloodPressure', 'Creatinine']

for i in range(30):
    patient_id = f'P{i+1:03d}'
    age = random.randint(15, 80)
    gender = random.choice(genders)
    diagnosis = random.choice(diagnoses)
    lab_values = {
        'HbA1c': round(random.uniform(4.0, 10.0), 1),
        'Cholesterol': round(random.uniform(150, 300), 1),
        'BloodPressure': round(random.uniform(80, 180), 1),
        'Creatinine': round(random.uniform(0.5, 2.0), 2)
    }
    patients.append([patient_id, age, gender, diagnosis, json.dumps(lab_values)])

with open(f'{WORKSPACE}/patients.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['patient_id', 'age', 'gender', 'diagnosis', 'lab_values_json'])
    writer.writerows(patients)
EOF

# Generate trial_criteria.json
python3 - <<EOF
import os; WORKSPACE = os.environ.get('WORKSPACE', os.getcwd())
import json

criteria = {
    "inclusion": {
        "age": {"min": 18, "max": 65},
        "gender": ["M", "F"],
        "diagnosis": ["diabetes", "hypertension"],
        "lab_values": {
            "HbA1c": {"max": 7.0},
            "Cholesterol": {"max": 240},
            "BloodPressure": {"max": 140}
        }
    },
    "exclusion": {
        "diagnosis": ["cancer"],
        "lab_values": {
            "Creatinine": {"max": 1.5}
        }
    }
}

with open(f'{WORKSPACE}/trial_criteria.json', 'w') as f:
    json.dump(criteria, f, indent=2)
EOF
