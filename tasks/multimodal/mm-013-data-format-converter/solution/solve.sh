#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

python - "$WORKSPACE" << 'PYEOF'
import sys
import json
import csv

ws = sys.argv[1]

with open(f"{ws}/schema.json") as f:
    schema = json.load(f)

with open(f"{ws}/input.csv", newline="") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

mappings = schema["mappings"]
result = []

for row in rows:
    obj = {}
    for m in mappings:
        raw = row[m["csv_column"]].strip()
        t = m["type"]
        if t == "integer":
            val = int(raw)
        elif t == "float":
            val = float(raw)
        elif t == "boolean":
            val = raw.lower() == "true"
        else:
            val = raw
        obj[m["json_field"]] = val
    result.append(obj)

with open(f"{ws}/output.json", "w") as f:
    json.dump(result, f, indent=2)
PYEOF
