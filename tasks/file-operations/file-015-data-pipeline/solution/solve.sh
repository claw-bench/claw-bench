#!/usr/bin/env bash
# Oracle solution for file-015-data-pipeline
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

python3 -c "
import csv
import json
import re
from datetime import datetime

def parse_date(date_str):
    \"\"\"Parse various date formats into YYYY-MM-DD.\"\"\"
    date_str = date_str.strip()
    # Try MM/DD/YYYY
    try:
        return datetime.strptime(date_str, '%m/%d/%Y').strftime('%Y-%m-%d')
    except ValueError:
        pass
    # Try DD-MM-YYYY
    try:
        return datetime.strptime(date_str, '%d-%m-%Y').strftime('%Y-%m-%d')
    except ValueError:
        pass
    # Try YYYY/MM/DD
    try:
        return datetime.strptime(date_str, '%Y/%m/%d').strftime('%Y-%m-%d')
    except ValueError:
        pass
    # Try Month DD, YYYY
    try:
        return datetime.strptime(date_str, '%B %d, %Y').strftime('%Y-%m-%d')
    except ValueError:
        pass
    raise ValueError(f'Cannot parse date: {date_str}')

# Read raw data
rows = []
with open('$WORKSPACE/raw_data.csv', newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

# Clean: remove rows with empty values
cleaned = []
for row in rows:
    if any(v.strip() == '' for v in row.values()):
        continue
    cleaned_row = {
        'name': row['name'].strip().title(),
        'city': row['city'].strip().title(),
        'date': parse_date(row['date']),
        'product': row['product'].strip(),
        'quantity': int(row['quantity'].strip()),
        'price': float(row['price'].strip()),
    }
    cleaned_row['total'] = round(cleaned_row['quantity'] * cleaned_row['price'], 2)
    cleaned.append(cleaned_row)

# Write clean CSV
with open('$WORKSPACE/clean_data.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['name', 'city', 'date', 'product', 'quantity', 'price', 'total'])
    writer.writeheader()
    for row in cleaned:
        writer.writerow(row)

# Write summary
cities = sorted(set(row['city'] for row in cleaned))
totals = [row['total'] for row in cleaned]
summary = {
    'total_rows': len(cleaned),
    'total_revenue': round(sum(totals), 2),
    'average_order': round(sum(totals) / len(totals), 2),
    'cities': cities,
}

with open('$WORKSPACE/summary.json', 'w') as f:
    json.dump(summary, f, indent=4)
"

echo "Solution written to $WORKSPACE/clean_data.csv and $WORKSPACE/summary.json"
