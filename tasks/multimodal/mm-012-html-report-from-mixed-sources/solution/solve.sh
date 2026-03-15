#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

python - "$WORKSPACE" << 'PYEOF'
import sys
import json
import csv

ws = sys.argv[1]

with open(f"{ws}/metadata.json") as f:
    meta = json.load(f)

with open(f"{ws}/text_summary.txt") as f:
    summary = f.read().strip()

with open(f"{ws}/data_table.csv", newline="") as f:
    reader = csv.reader(f)
    rows = list(reader)

headers = rows[0]
data_rows = rows[1:]

table_rows = "".join(
    "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>\n"
    for row in data_rows
)
header_cells = "".join(f"<th>{h}</th>" for h in headers)

html = f"""<!DOCTYPE html>
<html>
<head>
<title>{meta['title']}</title>
</head>
<body>
<h1>{meta['title']}</h1>
<h2>Report Metadata</h2>
<ul>
<li><strong>Author:</strong> {meta['author']}</li>
<li><strong>Date:</strong> {meta['date']}</li>
<li><strong>Department:</strong> {meta['department']}</li>
</ul>
<h2>Executive Summary</h2>
<p>{summary}</p>
<h2>Division Performance Data</h2>
<table>
<tr>{header_cells}</tr>
{table_rows}</table>
</body>
</html>
"""

with open(f"{ws}/combined_report.html", "w") as f:
    f.write(html)
PYEOF
