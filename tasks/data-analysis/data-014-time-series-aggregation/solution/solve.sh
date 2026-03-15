#!/usr/bin/env bash
# Oracle solution for data-014-time-series-aggregation
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

python - "$WORKSPACE" << 'PYEOF'
import sys
import csv
import json
from collections import defaultdict

ws = sys.argv[1]

# Read data
rows = []
with open(f'{ws}/metrics.csv', newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        row['cpu_percent'] = float(row['cpu_percent'])
        row['memory_mb'] = float(row['memory_mb'])
        row['requests_per_sec'] = float(row['requests_per_sec'])
        row['date'] = row['timestamp'].split(' ')[0]
        rows.append(row)

# Group by date
days = defaultdict(list)
for row in rows:
    days[row['date']].append(row)

daily = []
for date in sorted(days.keys()):
    records = days[date]
    cpus = [r['cpu_percent'] for r in records]
    mems = [r['memory_mb'] for r in records]
    reqs = [r['requests_per_sec'] for r in records]
    daily.append({
        'date': date,
        'avg_cpu': round(sum(cpus) / len(cpus), 2),
        'max_cpu': max(cpus),
        'avg_memory': round(sum(mems) / len(mems), 2),
        'total_requests': round(sum(reqs), 2)
    })

# Compute trends
def trend(first_val, last_val):
    if last_val > first_val * 1.05:
        return 'increasing'
    elif last_val < first_val * 0.95:
        return 'decreasing'
    else:
        return 'stable'

result = {
    'daily': daily,
    'trend': {
        'cpu': trend(daily[0]['avg_cpu'], daily[-1]['avg_cpu']),
        'memory': trend(daily[0]['avg_memory'], daily[-1]['avg_memory']),
        'requests': trend(daily[0]['total_requests'], daily[-1]['total_requests'])
    }
}

with open(f'{ws}/aggregated.json', 'w') as f:
    json.dump(result, f, indent=2)
PYEOF

echo "Aggregated report written to $WORKSPACE/aggregated.json"
