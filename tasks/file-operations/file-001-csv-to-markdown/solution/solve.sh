#!/usr/bin/env bash
# Oracle solution for file-001-csv-to-markdown
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

python3 -c "
import csv, sys

with open('$WORKSPACE/sample.csv', newline='') as f:
    reader = csv.reader(f)
    rows = list(reader)

header = rows[0]
lines = []
lines.append('| ' + ' | '.join(header) + ' |')
lines.append('| ' + ' | '.join(['---'] * len(header)) + ' |')
for row in rows[1:]:
    lines.append('| ' + ' | '.join(row) + ' |')

with open('$WORKSPACE/output.md', 'w') as f:
    f.write('\n'.join(lines) + '\n')
"

echo "Solution written to $WORKSPACE/output.md"
