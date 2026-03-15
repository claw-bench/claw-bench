#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${1:-workspace}"

python3 -c "
import re, csv

with open('$WORKSPACE/page.html') as f:
    html = f.read()

# Extract headers
headers = re.findall(r'<th>(.*?)</th>', html)

# Extract rows
rows = []
for tr in re.findall(r'<tr>\s*((?:<td>.*?</td>\s*)+)\s*</tr>', html, re.DOTALL):
    cells = re.findall(r'<td>(.*?)</td>', tr)
    if cells:
        rows.append(cells)

with open('$WORKSPACE/table_data.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(headers)
    writer.writerows(rows)
"

echo "Solution written to $WORKSPACE/table_data.csv"
