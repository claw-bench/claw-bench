#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
python3 -c "
import csv
from collections import defaultdict

with open('$WORKSPACE/sales.csv') as f:
    reader = csv.DictReader(f)
    totals = defaultdict(int)
    for row in reader:
        totals[row['category']] += int(row['amount'])

sorted_totals = sorted(totals.items(), key=lambda x: -x[1])

with open('$WORKSPACE/summary.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['category', 'total_amount'])
    for cat, total in sorted_totals:
        writer.writerow([cat, total])
"
echo "Solution written to $WORKSPACE/summary.csv"
