#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
python3 -c "
import csv, json, statistics

with open('$WORKSPACE/measurements.csv') as f:
    reader = csv.DictReader(f)
    rows = [(row['id'], float(row['value'])) for row in reader]

values = [v for _, v in rows]
q1, q2, q3 = statistics.quantiles(values, n=4)
iqr = q3 - q1
lb = q1 - 1.5 * iqr
ub = q3 + 1.5 * iqr

outliers = [(mid, mv) for mid, mv in rows if mv < lb or mv > ub]

with open('$WORKSPACE/outliers.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['id', 'value'])
    for mid, mv in outliers:
        writer.writerow([mid, mv])

analysis = {
    'q1': round(q1, 2),
    'q3': round(q3, 2),
    'iqr': round(iqr, 2),
    'lower_bound': round(lb, 2),
    'upper_bound': round(ub, 2),
    'outlier_count': len(outliers)
}
with open('$WORKSPACE/analysis.json', 'w') as f:
    json.dump(analysis, f, indent=2)
"
echo "Solution written"
