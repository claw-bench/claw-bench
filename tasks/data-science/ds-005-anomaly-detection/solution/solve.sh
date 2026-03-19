#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

python3 - <<EOF
import os; WORKSPACE = os.environ.get('WORKSPACE', os.getcwd())
import csv
import json
import math
from collections import defaultdict

input_path = f"{WORKSPACE}/sensor_data.csv"
output_path = f"{WORKSPACE}/anomalies.json"

# Load data grouped by sensor_id
sensor_values = defaultdict(list)

with open(input_path) as f:
    reader = csv.DictReader(f)
    for row in reader:
        sensor_values[row['sensor_id']].append({'timestamp': row['timestamp'], 'value': float(row['value'])})

result = {}

for sensor_id, readings in sensor_values.items():
    values = [r['value'] for r in readings]
    n = len(values)

    # IQR calculation
    sorted_vals = sorted(values)
    def percentile(data, p):
        k = (len(data)-1) * p
        f = math.floor(k)
        c = math.ceil(k)
        if f == c:
            return data[int(k)]
        d0 = data[int(f)] * (c - k)
        d1 = data[int(c)] * (k - f)
        return d0 + d1

    Q1 = percentile(sorted_vals, 0.25)
    Q3 = percentile(sorted_vals, 0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    iqr_anomalies = []
    for r in readings:
        if r['value'] < lower_bound or r['value'] > upper_bound:
            iqr_anomalies.append({'timestamp': r['timestamp'], 'value': r['value']})

    # Z-score calculation
    mean = sum(values) / n
    variance = sum((x - mean) ** 2 for x in values) / n
    stddev = math.sqrt(variance)

    zscore_anomalies = []
    if stddev > 0:
        for r in readings:
            z = (r['value'] - mean) / stddev
            if abs(z) > 3:
                zscore_anomalies.append({'timestamp': r['timestamp'], 'value': r['value']})
    else:
        # No variation, no anomalies by zscore
        zscore_anomalies = []

    anomaly_rate = {
        'iqr': len(iqr_anomalies) / n,
        'zscore': len(zscore_anomalies) / n
    }

    result[sensor_id] = {
        'iqr_anomalies': iqr_anomalies,
        'zscore_anomalies': zscore_anomalies,
        'anomaly_rate': anomaly_rate
    }

with open(output_path, 'w') as f:
    json.dump(result, f, indent=2)
EOF
