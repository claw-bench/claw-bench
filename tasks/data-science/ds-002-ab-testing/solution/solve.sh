#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

python3 - <<EOF
import os; WORKSPACE = os.environ.get('WORKSPACE', os.getcwd())
import csv
import json
from math import sqrt
from scipy.stats import chi2_contingency

input_file = f"{WORKSPACE}/ab_test.csv"
output_file = f"{WORKSPACE}/ab_results.json"

# Read data
control_converted = 0
control_total = 0

treatment_converted = 0

treatment_total = 0

with open(input_file, newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        group = row['group']
        converted = int(row['converted'])
        if group == 'control':
            control_total += 1
            control_converted += converted
        elif group == 'treatment':
            treatment_total += 1
            treatment_converted += converted

control_rate = control_converted / control_total if control_total > 0 else 0

treatment_rate = treatment_converted / treatment_total if treatment_total > 0 else 0

# Contingency table
# Rows: group (control, treatment)
# Columns: converted (yes=1, no=0)
contingency = [
    [control_converted, control_total - control_converted],
    [treatment_converted, treatment_total - treatment_converted]
]

chi2, p_value, _, _ = chi2_contingency(contingency, correction=False)

lift = (treatment_rate - control_rate) / control_rate if control_rate > 0 else 0

significant = p_value < 0.05

recommendation = "Implement treatment" if significant and lift > 0 else "Do not implement treatment"

# Write output
result = {
    "control_rate": control_rate,
    "treatment_rate": treatment_rate,
    "lift": lift,
    "chi2": chi2,
    "p_value": p_value,
    "significant": significant,
    "recommendation": recommendation
}

with open(output_file, 'w') as f:
    json.dump(result, f, indent=2)
EOF
