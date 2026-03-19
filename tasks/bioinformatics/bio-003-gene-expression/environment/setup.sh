#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

mkdir -p "$WORKSPACE"

python3 - <<EOF
import os; WORKSPACE = os.environ.get('WORKSPACE', os.getcwd())
import csv
import random
import numpy as np
random.seed(42)
np.random.seed(42)

# Parameters
num_genes = 50
num_control = 10
num_treated = 10

# Gene names
genes = [f"Gene{i+1}" for i in range(num_genes)]

# Sample names
control_samples = [f"Sample{j+1}_Control" for j in range(num_control)]
treated_samples = [f"Sample{j+1}_Treated" for j in range(num_treated)]

header = ["gene"] + control_samples + treated_samples

# Generate expression data
# Control samples: expression ~ Poisson with lambda 20
# Treated samples: for 30 genes, increase mean by factor 2 (upregulated), for others no change

expression_data = []
for i, gene in enumerate(genes):
    # Base mean expression
    base_mean = 20
    # Upregulate first 30 genes in treated
    if i < 30:
        treated_mean = base_mean * 2
    else:
        treated_mean = base_mean

    control_expr = np.random.poisson(lam=base_mean, size=num_control)
    treated_expr = np.random.poisson(lam=treated_mean, size=num_treated)

    row = [gene] + control_expr.tolist() + treated_expr.tolist()
    expression_data.append(row)

# Write CSV
with open(f"{WORKSPACE}/expression_matrix.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(expression_data)
EOF
