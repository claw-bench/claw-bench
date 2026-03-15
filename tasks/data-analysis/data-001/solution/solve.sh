#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
python3 -c "
import csv, json, statistics

with open('$WORKSPACE/numbers.csv') as f:
    reader = csv.DictReader(f)
    values = [float(row['value']) for row in reader]

result = {
    'mean': round(statistics.mean(values), 2),
    'median': round(statistics.median(values), 2),
    'mode': round(statistics.mode(values), 2),
    'std_dev': round(statistics.pstdev(values), 2)
}

with open('$WORKSPACE/stats.json', 'w') as f:
    json.dump(result, f, indent=2)
"
echo "Solution written to $WORKSPACE/stats.json"
