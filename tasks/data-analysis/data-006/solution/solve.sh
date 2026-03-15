#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
python3 -c "
import csv
from collections import defaultdict
from datetime import date

with open('$WORKSPACE/daily_sales.csv') as f:
    reader = csv.DictReader(f)
    rows = [(row['date'], float(row['amount'])) for row in reader]

weekly = defaultdict(float)
monthly = defaultdict(float)
for d_str, amt in rows:
    d = date.fromisoformat(d_str)
    iso = d.isocalendar()
    wk = f'{iso[0]}-W{iso[1]:02d}'
    weekly[wk] += amt
    monthly[d_str[:7]] += amt

with open('$WORKSPACE/weekly.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['week', 'total_amount'])
    for wk in sorted(weekly):
        writer.writerow([wk, round(weekly[wk], 2)])

with open('$WORKSPACE/monthly.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['month', 'total_amount'])
    for m in sorted(monthly):
        writer.writerow([m, round(monthly[m], 2)])
"
echo "Solution written"
