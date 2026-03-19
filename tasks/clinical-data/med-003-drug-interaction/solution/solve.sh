#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

python3 - <<EOF
import os; WORKSPACE = os.environ.get('WORKSPACE', os.getcwd())
import csv
import json
from collections import defaultdict

# Read patient medications
patient_meds = defaultdict(set)
with open(f"{WORKSPACE}/patient_medications.csv", newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        pid = row['patient_id']
        med = row['medication'].lower()
        patient_meds[pid].add(med)

# Read interaction database
interaction_db = {}
with open(f"{WORKSPACE}/interaction_db.csv", newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        a = row['drug_a'].lower()
        b = row['drug_b'].lower()
        key = tuple(sorted([a, b]))
        interaction_db[key] = {
            'severity': row['severity'],
            'effect': row['effect']
        }

# For each patient, find interactions
report = {}
for pid, meds in patient_meds.items():
    meds_list = sorted(meds)
    interactions = []
    for i in range(len(meds_list)):
        for j in range(i+1, len(meds_list)):
            pair = (meds_list[i], meds_list[j])
            if pair in interaction_db:
                inter = interaction_db[pair]
                interactions.append({
                    'drug_a': pair[0].capitalize(),
                    'drug_b': pair[1].capitalize(),
                    'severity': inter['severity'],
                    'effect': inter['effect']
                })
    report[pid] = interactions

# Write JSON report
with open(f"{WORKSPACE}/interaction_report.json", "w") as f:
    json.dump(report, f, indent=2)
EOF
