#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

python3 - <<EOF
import os; WORKSPACE = os.environ.get('WORKSPACE', os.getcwd())
import csv
import json

input_path = f"{WORKSPACE}/lab_results.csv"
output_path = f"{WORKSPACE}/clinical_alerts.json"

alerts = []

with open(input_path, newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        patient_id = row['patient_id']
        test_name = row['test_name']
        value = float(row['value'])
        unit = row['unit']
        reference_low = float(row['reference_low'])
        reference_high = float(row['reference_high'])

        range_width = reference_high - reference_low

        if value < reference_low or value > reference_high:
            if value < reference_low:
                diff = reference_low - value
            else:
                diff = value - reference_high

            percentage = diff / range_width

            if percentage <= 0.20:
                severity = "mild"
            elif percentage <= 0.50:
                severity = "moderate"
            else:
                severity = "severe"

            alert = {
                "patient_id": patient_id,
                "test_name": test_name,
                "value": value,
                "unit": unit,
                "severity": severity
            }
            alerts.append(alert)

with open(output_path, "w") as f:
    json.dump(alerts, f, indent=2)
EOF
