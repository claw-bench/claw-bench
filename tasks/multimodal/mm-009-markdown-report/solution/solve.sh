#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
mkdir -p "$WORKSPACE"

python - "$WORKSPACE" << 'PYEOF'
import csv
import json
import sys
from datetime import date
from collections import defaultdict

ws = sys.argv[1]

# Read sales data
totals = defaultdict(float)
with open(f'{ws}/sales.csv', newline='') as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    for row in rows:
        totals[row['salesperson']] += float(row['amount'])

# Read targets
with open(f'{ws}/targets.json') as f:
    targets_data = json.load(f)
targets = targets_data['targets']

# Compute metrics
ytd_total = sum(totals.values())
months = len(set(r['month'] for r in rows))
avg_monthly = ytd_total / months

# Top performer
top_performer = max(totals, key=totals.get)
top_performer_total = totals[top_performer]

# Build sales table sorted by YTD total descending
sorted_people = sorted(totals.items(), key=lambda x: x[1], reverse=True)
table_lines = []
table_lines.append('| Salesperson | YTD Total | Target | % to Target |')
table_lines.append('| --- | --- | --- | --- |')
for name, total in sorted_people:
    target = targets[name]
    pct = (total / target) * 100
    table_lines.append(f'| {name} | {total:,.0f} | {target:,.0f} | {pct:.1f}% |')
sales_table = '\n'.join(table_lines)

# Read template
with open(f'{ws}/template.md') as f:
    template = f.read()

# Fill placeholders
report = template.replace('{{REPORT_DATE}}', date.today().isoformat())
report = report.replace('{{YTD_TOTAL}}', f'{ytd_total:,.0f}')
report = report.replace('{{AVG_MONTHLY}}', f'{avg_monthly:,.2f}')
report = report.replace('{{TOP_PERFORMER_TOTAL}}', f'{top_performer_total:,.0f}')
report = report.replace('{{TOP_PERFORMER}}', top_performer)
report = report.replace('{{SALES_TABLE}}', sales_table)

with open(f'{ws}/report.md', 'w') as f:
    f.write(report)
PYEOF

echo "Solution written to $WORKSPACE/report.md"
