#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

python - "$WORKSPACE" << 'PYEOF'
import sys
import json

ws = sys.argv[1]

with open(f"{ws}/before.json") as f:
    before = json.load(f)

with open(f"{ws}/after.json") as f:
    after = json.load(f)

additions = []
removals = []
modifications = []

def compare(b, a, prefix=""):
    all_keys = set(list(b.keys()) + list(a.keys()))
    for key in all_keys:
        path = f"{prefix}.{key}" if prefix else key
        in_b = key in b
        in_a = key in a
        if in_b and not in_a:
            removals.append({"path": path, "value": b[key]})
        elif in_a and not in_b:
            additions.append({"path": path, "value": a[key]})
        else:
            bv = b[key]
            av = a[key]
            if isinstance(bv, dict) and isinstance(av, dict):
                compare(bv, av, path)
            elif bv != av:
                modifications.append({"path": path, "old_value": bv, "new_value": av})

compare(before, after)

additions.sort(key=lambda x: x["path"])
removals.sort(key=lambda x: x["path"])
modifications.sort(key=lambda x: x["path"])

report = {
    "additions": additions,
    "removals": removals,
    "modifications": modifications
}

with open(f"{ws}/diff_report.json", "w") as f:
    json.dump(report, f, indent=2)
PYEOF
