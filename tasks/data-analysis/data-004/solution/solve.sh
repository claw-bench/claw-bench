#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
python3 -c "
import csv
from collections import defaultdict

with open('$WORKSPACE/transactions.csv') as f:
    reader = csv.DictReader(f)
    pivot = defaultdict(lambda: defaultdict(float))
    categories = set()
    for row in reader:
        month = row['date'][:7]
        cat = row['category']
        pivot[month][cat] += float(row['amount'])
        categories.add(cat)

cats = sorted(categories)
months_sorted = sorted(pivot.keys())

with open('$WORKSPACE/pivot.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['month'] + cats)
    totals = {c: 0 for c in cats}
    for m in months_sorted:
        row = [m]
        for c in cats:
            val = round(pivot[m][c], 2)
            row.append(val)
            totals[c] += val
        writer.writerow(row)
    writer.writerow(['Total'] + [round(totals[c], 2) for c in cats])
"
echo "Solution written to $WORKSPACE/pivot.csv"
