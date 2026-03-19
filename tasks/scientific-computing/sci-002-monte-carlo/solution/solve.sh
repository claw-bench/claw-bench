#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

python3 - <<'EOF'
import os; WORKSPACE = os.environ.get('WORKSPACE', os.getcwd())
import math
import random
import csv
import json

random.seed(42)

sample_sizes = [100, 1000, 10000, 100000, 1000000]
true_pi = math.pi

results = []

for n in sample_sizes:
    inside = 0
    for _ in range(n):
        x = random.uniform(0, 1)
        y = random.uniform(0, 1)
        if x*x + y*y <= 1:
            inside += 1
    estimate = 4 * inside / n
    error = abs(estimate - true_pi)
    results.append({'n': n, 'estimate': estimate, 'error': error})

# Compute convergence rates
convergence_rates = [None]
for i in range(1, len(results)):
    e1 = results[i-1]['error']
    e2 = results[i]['error']
    n1 = results[i-1]['n']
    n2 = results[i]['n']
    if e2 == 0 or e1 == 0:
        rate = None
    else:
        rate = (math.log(e1 / e2) / math.log(n2 / n1))
    convergence_rates.append(rate)

# Write mc_results.csv
csv_path = f"{WORKSPACE}/mc_results.csv"
with open(csv_path, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['n', 'estimate', 'error', 'convergence_rate'])
    for i, res in enumerate(results):
        conv = convergence_rates[i]
        conv_str = 'null' if conv is None else f'{conv:.6f}'
        writer.writerow([
            res['n'],
            f'{res["estimate"]:.6f}',
            f'{res["error"]:.6f}',
            conv_str
        ])

# Write mc_summary.json
json_path = f"{WORKSPACE}/mc_summary.json"
summary = {
    'true_pi': true_pi,
    'estimates': [r['estimate'] for r in results],
    'errors': [r['error'] for r in results],
    'convergence_rates': [None if c is None else c for c in convergence_rates]
}
with open(json_path, 'w') as f:
    json.dump(summary, f, indent=2)
EOF
