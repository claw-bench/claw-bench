#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

python3 - <<'EOF'
import os; WORKSPACE = os.environ.get('WORKSPACE', os.getcwd())
import csv
import json
import numpy as np
from scipy import stats

input_file = f"{WORKSPACE}/experiment_data.csv"
results_file = f"{WORKSPACE}/stats_results.csv"
summary_file = f"{WORKSPACE}/stats_summary.json"

# Read data
groups = {}
with open(input_file) as f:
    reader = csv.DictReader(f)
    for row in reader:
        g = row['group']
        val = float(row['measurement'])
        groups.setdefault(g, []).append(val)

group_names = list(groups.keys())
measurements = [np.array(groups[g]) for g in group_names]

alpha = 0.05

if len(group_names) == 2:
    # t-test (Welch's)
    stat, p_value = stats.ttest_ind(measurements[0], measurements[1], equal_var=False)
    # Cohen's d
    n1, n2 = len(measurements[0]), len(measurements[1])
    mean1, mean2 = measurements[0].mean(), measurements[1].mean()
    s1, s2 = measurements[0].std(ddof=1), measurements[1].std(ddof=1)
    s_pooled = ((n1 -1)*s1**2 + (n2 -1)*s2**2) / (n1 + n2 -2)
    cohen_d = abs((mean1 - mean2) / (s_pooled ** 0.5)) if s_pooled > 0 else 0.0
    test_name = 't-test'
    effect_size = cohen_d
else:
    # ANOVA
    stat, p_value = stats.f_oneway(*measurements)
    # Eta squared
    all_values = np.concatenate(measurements)
    grand_mean = all_values.mean()
    ss_between = sum(len(m) * (m.mean() - grand_mean)**2 for m in measurements)
    ss_total = ((all_values - grand_mean)**2).sum()
    eta_sq = ss_between / ss_total if ss_total > 0 else 0.0
    test_name = 'ANOVA'
    effect_size = eta_sq

significant = p_value < alpha

# Write results CSV
with open(results_file, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['test', 'statistic', 'p_value', 'effect_size', 'significant'])
    writer.writerow([
        test_name,
        f"{stat:.4f}",
        f"{p_value:.6f}",
        f"{effect_size:.4f}",
        str(significant).lower()
    ])

# Write summary JSON
summary = {
    'test': test_name,
    'statistic': round(float(stat), 4),
    'p_value': round(float(p_value), 6),
    'effect_size': round(float(effect_size), 4),
    'significant': significant
}

with open(summary_file, 'w') as f:
    json.dump(summary, f, indent=2)
EOF
