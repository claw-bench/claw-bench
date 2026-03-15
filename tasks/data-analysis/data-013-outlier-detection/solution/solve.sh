#!/usr/bin/env bash
# Oracle solution for data-013-outlier-detection
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

python - "$WORKSPACE" << 'PYEOF'
import sys
import csv
import json
import math
from collections import defaultdict

ws = sys.argv[1]

# Read data
rows = []
with open(f'{ws}/measurements.csv', newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        row['value'] = float(row['value'])
        rows.append(row)

total_records = len(rows)

# Group by sensor
sensors = defaultdict(list)
for row in rows:
    sensors[row['sensor_id']].append(row)

outliers = []
summary_by_sensor = {}

for sid, readings in sorted(sensors.items()):
    values = [r['value'] for r in readings]
    n = len(values)
    sv = sorted(values)

    # Q1 and Q3 using linear interpolation (exclusive method)
    def percentile(data, p):
        k = (len(data) - 1) * p / 100.0
        f = math.floor(k)
        c = math.ceil(k)
        if f == c:
            return data[int(k)]
        return data[f] * (c - k) + data[c] * (k - f)

    q1 = percentile(sv, 25)
    q3 = percentile(sv, 75)
    iqr = q3 - q1

    mean = sum(values) / n
    std = (sum((v - mean) ** 2 for v in values) / n) ** 0.5

    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    sensor_outliers = []
    for r in readings:
        v = r['value']
        if v < lower or v > upper:
            z = round((v - mean) / std, 2) if std > 0 else 0.0
            sensor_outliers.append({
                'sensor_id': r['sensor_id'],
                'timestamp': r['timestamp'],
                'value': v,
                'z_score': z
            })

    outliers.extend(sensor_outliers)

    summary_by_sensor[sid] = {
        'total_readings': n,
        'outlier_count': len(sensor_outliers),
        'mean': round(mean, 2),
        'std': round(std, 2),
        'q1': round(q1, 2),
        'q3': round(q3, 2)
    }

# Sort outliers by absolute z-score descending
outliers.sort(key=lambda x: abs(x['z_score']), reverse=True)

result = {
    'total_records': total_records,
    'outlier_count': len(outliers),
    'outliers': outliers,
    'summary_by_sensor': summary_by_sensor
}

with open(f'{ws}/outlier_report.json', 'w') as f:
    json.dump(result, f, indent=2)
PYEOF

echo "Outlier report written to $WORKSPACE/outlier_report.json"
