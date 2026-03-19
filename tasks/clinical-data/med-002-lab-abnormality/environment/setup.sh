#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

mkdir -p "$WORKSPACE"

python3 - <<EOF
import os; WORKSPACE = os.environ.get('WORKSPACE', os.getcwd())
import csv
import random
random.seed(42)

# Define some patients and tests
patients = [f"P{str(i).zfill(3)}" for i in range(1, 26)]
tests = [
    {"test_name": "Hemoglobin", "unit": "g/dL", "ref_low": 12.0, "ref_high": 16.0},
    {"test_name": "WBC", "unit": "10^3/uL", "ref_low": 4.0, "ref_high": 11.0},
    {"test_name": "Platelets", "unit": "10^3/uL", "ref_low": 150, "ref_high": 400},
    {"test_name": "Glucose", "unit": "mg/dL", "ref_low": 70, "ref_high": 99},
    {"test_name": "Creatinine", "unit": "mg/dL", "ref_low": 0.6, "ref_high": 1.3},
    {"test_name": "Sodium", "unit": "mmol/L", "ref_low": 135, "ref_high": 145},
    {"test_name": "Potassium", "unit": "mmol/L", "ref_low": 3.5, "ref_high": 5.1},
]

rows = []

# Generate realistic lab results with some abnormal values
for patient in patients:
    for test in tests:
        ref_low = test["ref_low"]
        ref_high = test["ref_high"]
        range_width = ref_high - ref_low

        # 70% chance normal, 30% chance abnormal
        if random.random() < 0.7:
            # Normal value within reference range
            value = random.uniform(ref_low, ref_high)
        else:
            # Abnormal value
            # Decide if low or high abnormal
            if random.random() < 0.5:
                # Low abnormal: up to 70% below ref_low
                value = ref_low - random.uniform(0.05 * range_width, 0.7 * range_width)
            else:
                # High abnormal: up to 70% above ref_high
                value = ref_high + random.uniform(0.05 * range_width, 0.7 * range_width)

        # Round value reasonably
        if isinstance(ref_low, int) and isinstance(ref_high, int):
            value = round(value)
        else:
            value = round(value, 2)

        rows.append({
            "patient_id": patient,
            "test_name": test["test_name"],
            "value": value,
            "unit": test["unit"],
            "reference_low": ref_low,
            "reference_high": ref_high
        })

with open(f"{WORKSPACE}/lab_results.csv", "w", newline='') as f:
    writer = csv.DictWriter(f, fieldnames=["patient_id", "test_name", "value", "unit", "reference_low", "reference_high"])
    writer.writeheader()
    writer.writerows(rows)
EOF
