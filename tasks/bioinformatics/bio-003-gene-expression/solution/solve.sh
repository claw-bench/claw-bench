#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

python3 - <<EOF
import os; WORKSPACE = os.environ.get('WORKSPACE', os.getcwd())
import csv
import json
import math
from scipy.stats import ttest_ind

input_file = f"{WORKSPACE}/expression_matrix.csv"
deg_file = f"{WORKSPACE}/deg_results.csv"
summary_file = f"{WORKSPACE}/expression_summary.json"

# Read expression matrix
with open(input_file, newline="") as f:
    reader = csv.reader(f)
    header = next(reader)
    data = list(reader)

# Identify control and treated indices
control_indices = [i for i, h in enumerate(header) if h.endswith("_Control")]
treated_indices = [i for i, h in enumerate(header) if h.endswith("_Treated")]

results = []

for row in data:
    gene = row[0]
    expr_vals = list(map(float, row[1:]))

    # Extract control and treated values
    control_vals = [expr_vals[i-1] for i in control_indices]  # -1 because expr_vals excludes gene col
    treated_vals = [expr_vals[i-1] for i in treated_indices]

    # Normalize using log2(x+1)
    control_log = [math.log2(x + 1) for x in control_vals]
    treated_log = [math.log2(x + 1) for x in treated_vals]

    # Compute fold-change on original scale (mean treated / mean control)
    mean_control = sum(control_vals) / len(control_vals) if len(control_vals) > 0 else 0
    mean_treated = sum(treated_vals) / len(treated_vals) if len(treated_vals) > 0 else 0
    fold_change = mean_treated / mean_control if mean_control != 0 else float('inf')

    # Perform two-sided t-test unequal variance on log normalized values
    try:
        t_stat, p_value = ttest_ind(treated_log, control_log, equal_var=False)
    except Exception:
        p_value = 1.0

    significant = p_value < 0.05

    results.append({
        "gene": gene,
        "fold_change": round(fold_change, 4),
        "p_value": round(p_value, 6),
        "significant": str(significant)
    })

# Write deg_results.csv
with open(deg_file, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["gene", "fold_change", "p_value", "significant"])
    writer.writeheader()
    for r in results:
        writer.writerow(r)

# Prepare summary
total_genes = len(results)
significant_genes = [r for r in results if r["significant"] == "True"]
num_significant = len(significant_genes)
if num_significant > 0:
    mean_fc_sig = sum(r["fold_change"] for r in significant_genes) / num_significant
else:
    mean_fc_sig = 0.0

summary = {
    "total_genes": total_genes,
    "significant_genes": num_significant,
    "mean_fold_change_significant": mean_fc_sig
}

with open(summary_file, "w") as f:
    json.dump(summary, f, indent=2)
EOF
