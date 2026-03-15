#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
python3 -c "
import csv

with open('$WORKSPACE/people.csv') as f:
    reader = csv.DictReader(f)
    rows = [row for row in reader if int(row['age']) > 25]

rows.sort(key=lambda r: r['name'])

with open('$WORKSPACE/filtered.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['name', 'age', 'city', 'score'])
    writer.writeheader()
    writer.writerows(rows)
"
echo "Solution written to $WORKSPACE/filtered.csv"
