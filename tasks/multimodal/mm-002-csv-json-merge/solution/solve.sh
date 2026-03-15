#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

python - "$WORKSPACE" << 'PYEOF'
import csv, json, sys

ws = sys.argv[1]

with open(f'{ws}/employees.csv') as f:
    reader = csv.DictReader(f)
    employees = list(reader)

with open(f'{ws}/performance.json') as f:
    reviews = json.load(f)

# Group reviews by employee_id
review_map = {}
for r in reviews:
    eid = r['employee_id']
    entry = {k: v for k, v in r.items() if k != 'employee_id'}
    review_map.setdefault(eid, []).append(entry)

# Merge
combined = []
for emp in employees:
    record = dict(emp)
    record['performance_reviews'] = review_map.get(emp['employee_id'], [])
    combined.append(record)

combined.sort(key=lambda x: x['employee_id'])

with open(f'{ws}/combined.json', 'w') as f:
    json.dump(combined, f, indent=2)
    f.write('\n')
PYEOF
