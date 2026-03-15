#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
python3 -c "
import csv, json
from collections import defaultdict

all_rows = []
for q_name, q_label in [('q1','Q1'), ('q2','Q2'), ('q3','Q3')]:
    with open(f'$WORKSPACE/{q_name}.csv') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row['quarter'] = q_label
            all_rows.append(row)

with open('$WORKSPACE/merged.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['product','region','revenue','units','quarter'])
    writer.writeheader()
    writer.writerows(all_rows)

# Compute trends
prod_rev = defaultdict(lambda: defaultdict(float))
for row in all_rows:
    prod_rev[row['product']][row['quarter']] += float(row['revenue'])

trends = []
for prod in sorted(prod_rev.keys()):
    q1r = prod_rev[prod]['Q1']
    q2r = prod_rev[prod]['Q2']
    q3r = prod_rev[prod]['Q3']
    g12 = round((q2r - q1r) / q1r * 100, 2)
    g23 = round((q3r - q2r) / q2r * 100, 2)
    trends.append({'product': prod, 'q1_to_q2_growth': g12, 'q2_to_q3_growth': g23})

with open('$WORKSPACE/trends.json', 'w') as f:
    json.dump(trends, f, indent=2)
"
echo "Solution written"
