#!/usr/bin/env bash
# Oracle solution for file-012-csv-stats
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

python3 -c "
import csv
import json
import statistics

prices = []
with open('$WORKSPACE/sales.csv', newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        prices.append(float(row['price']))

stats = {
    'min': round(min(prices), 2),
    'max': round(max(prices), 2),
    'mean': round(statistics.mean(prices), 2),
    'median': round(statistics.median(prices), 2),
}

with open('$WORKSPACE/stats.json', 'w') as f:
    json.dump(stats, f, indent=4)
"

echo "Solution written to $WORKSPACE/stats.json"
