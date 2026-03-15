#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
python3 -c "
import csv, json, re
from statistics import median
from datetime import datetime

with open('$WORKSPACE/dirty_data.csv') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

# Drop rows with missing id or name
rows_dropped = 0
valid = []
for r in rows:
    if not r['id'].strip() or not r['name'].strip():
        rows_dropped += 1
    else:
        valid.append(r)

# Remove duplicates by id (keep first)
seen = set()
deduped = []
dups = 0
for r in valid:
    rid = r['id'].strip()
    if rid in seen:
        dups += 1
    else:
        seen.add(rid)
        deduped.append(r)

# Fill missing salaries with median
salaries = [int(r['salary']) for r in deduped if r['salary'].strip()]
med_sal = median(salaries)
filled = 0
for r in deduped:
    if not r['salary'].strip():
        r['salary'] = str(int(med_sal))
        filled += 1

# Normalize email
for r in deduped:
    r['email'] = r['email'].strip().lower()

# Normalize phone
for r in deduped:
    digits = re.sub(r'\D', '', r['phone'])
    if len(digits) == 11 and digits.startswith('1'):
        digits = digits[1:]
    r['phone'] = digits

# Normalize date
def parse_date(s):
    s = s.strip()
    for fmt in ['%m/%d/%Y', '%d-%m-%Y', '%Y-%m-%d']:
        try:
            return datetime.strptime(s, fmt).strftime('%Y-%m-%d')
        except ValueError:
            continue
    return s

for r in deduped:
    r['date_joined'] = parse_date(r['date_joined'])

deduped.sort(key=lambda r: int(r['id']))

with open('$WORKSPACE/clean_data.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['id','name','email','phone','date_joined','salary'])
    writer.writeheader()
    writer.writerows(deduped)

report = {
    'duplicates_removed': dups,
    'missing_values_filled': filled,
    'rows_dropped': rows_dropped,
    'total_clean_rows': len(deduped)
}
with open('$WORKSPACE/cleaning_report.json', 'w') as f:
    json.dump(report, f, indent=2)
"
echo "Solution written"
