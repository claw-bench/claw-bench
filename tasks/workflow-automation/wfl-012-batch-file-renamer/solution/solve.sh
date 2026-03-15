#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

python - "$WORKSPACE" << 'PYEOF'
import sys, json, re
ws = sys.argv[1]

with open(f"{ws}/file_list.json") as f:
    files = json.load(f)

with open(f"{ws}/rename_rules.json") as f:
    rules = json.load(f)

results = []
for filename in files:
    new_name = filename
    for rule in rules:
        new_name = re.sub(rule["pattern"], rule["replacement"], new_name)
    results.append({"original": filename, "renamed": new_name})

with open(f"{ws}/new_names.json", "w") as f:
    json.dump(results, f, indent=2)
PYEOF
