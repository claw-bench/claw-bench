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

num_users = 1000

# Assign roughly half to control and half to treatment
users = list(range(1, num_users + 1))

# Conversion rates
control_rate = 0.10
# Treatment has slightly better conversion
treatment_rate = 0.13

rows = []
for user_id in users:
    group = 'control' if user_id <= num_users // 2 else 'treatment'
    if group == 'control':
        converted = 1 if random.random() < control_rate else 0
    else:
        converted = 1 if random.random() < treatment_rate else 0
    rows.append({'user_id': user_id, 'group': group, 'converted': converted})

with open(f'{WORKSPACE}/ab_test.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['user_id', 'group', 'converted'])
    writer.writeheader()
    writer.writerows(rows)
EOF
