#!/usr/bin/env bash
# Oracle solution for wfl-003-multi-step-data-pipeline
set -euo pipefail

WORKSPACE="${1:-workspace}"

python3 -c "
import csv
import json
import os

ws = '$WORKSPACE'
os.makedirs(f'{ws}/pipeline_output', exist_ok=True)

# Step 1: Read CSV
with open(f'{ws}/data.csv', newline='') as f:
    reader = csv.DictReader(f)
    raw_data = []
    for row in reader:
        row['amount'] = float(row['amount'])
        row['quantity'] = int(row['quantity'])
        row['id'] = int(row['id'])
        raw_data.append(row)

with open(f'{ws}/pipeline_output/step1_raw.json', 'w') as f:
    json.dump(raw_data, f, indent=2)

# Step 2: Filter rows where amount > 100
filtered = [r for r in raw_data if r['amount'] > 100]
with open(f'{ws}/pipeline_output/step2_filtered.json', 'w') as f:
    json.dump(filtered, f, indent=2)

# Step 3: Compute stats
amounts = [r['amount'] for r in filtered]
stats = {
    'total_amount': sum(amounts),
    'average_amount': round(sum(amounts) / len(amounts), 2),
    'count': len(filtered),
    'max_amount': max(amounts),
    'min_amount': min(amounts)
}
with open(f'{ws}/pipeline_output/step3_stats.json', 'w') as f:
    json.dump(stats, f, indent=2)

# Step 4: Write report
report_lines = [
    'Sales Data Pipeline Report',
    '=' * 40,
    f'Total records processed: {len(raw_data)}',
    f'Records after filtering (amount > 100): {stats[\"count\"]}',
    '',
    'Statistics on filtered data:',
    f'  Total amount: {stats[\"total_amount\"]}',
    f'  Average amount: {stats[\"average_amount\"]}',
    f'  Maximum amount: {stats[\"max_amount\"]}',
    f'  Minimum amount: {stats[\"min_amount\"]}',
    f'  Count: {stats[\"count\"]}',
]
with open(f'{ws}/pipeline_output/step4_report.txt', 'w') as f:
    f.write('\n'.join(report_lines) + '\n')
"

echo "Pipeline complete. Outputs in $WORKSPACE/pipeline_output/"
