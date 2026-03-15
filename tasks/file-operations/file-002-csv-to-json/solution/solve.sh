#!/usr/bin/env bash
# Oracle solution for file-002-csv-to-json
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

python3 -c "
import csv, json

with open('$WORKSPACE/data.csv', newline='') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

with open('$WORKSPACE/output.json', 'w') as f:
    json.dump(rows, f, indent=2)
"

echo "Solution written to $WORKSPACE/output.json"
