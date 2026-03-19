#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

mkdir -p "$WORKSPACE"

python3 - <<'EOF'
import os; WORKSPACE = os.environ.get('WORKSPACE', os.getcwd())
import csv
import random
import numpy as np
random.seed(42)
np.random.seed(42)

# Generate synthetic experimental data
# Randomly decide to create either 2 or 3 groups
num_groups = random.choice([2, 3])
groups = []
if num_groups == 2:
    groups = ['Control', 'Treatment']
else:
    groups = ['Control', 'Treatment1', 'Treatment2']

rows = []

# Generate measurements with some differences between groups
for group in groups:
    if group == 'Control':
        # Control group around mean 50
        data = np.random.normal(loc=50, scale=5, size=25)
    elif group == 'Treatment':
        # Treatment group mean shifted by +5
        data = np.random.normal(loc=55, scale=5, size=25)
    elif group == 'Treatment1':
        data = np.random.normal(loc=52, scale=5, size=20)
    elif group == 'Treatment2':
        data = np.random.normal(loc=58, scale=5, size=20)
    else:
        data = np.random.normal(loc=50, scale=5, size=20)
    for val in data:
        rows.append([group, f"{val:.4f}"])

# Shuffle rows
random.shuffle(rows)

with open(f"{WORKSPACE}/experiment_data.csv", "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['group', 'measurement'])
    writer.writerows(rows)
EOF
