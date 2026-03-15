#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

python - "$WORKSPACE" << 'PYEOF'
import sys, json

ws = sys.argv[1]

statements = []
with open(f"{ws}/updates.jsonl") as f:
    for line in f:
        line = line.strip()
        if line:
            statements.append(json.loads(line))

# Track first and latest values for each (subject, attribute)
first_values = {}
current_values = {}
source_ids = {}

for stmt in statements:
    key = (stmt["subject"], stmt["attribute"])
    if key not in first_values:
        first_values[key] = stmt["value"]
    current_values[key] = stmt["value"]
    source_ids[key] = stmt["id"]

facts = []
updates_count = 0
for key in sorted(current_values.keys()):
    subject, attribute = key
    was_updated = first_values[key] != current_values[key]
    if was_updated:
        updates_count += 1
    fact = {
        "subject": subject,
        "attribute": attribute,
        "current_value": current_values[key],
        "was_updated": was_updated,
        "source_id": source_ids[key]
    }
    if was_updated:
        fact["original_value"] = first_values[key]
    facts.append(fact)

result = {
    "facts": facts,
    "total_statements": len(statements),
    "total_unique_facts": len(current_values),
    "total_updates": updates_count
}

with open(f"{ws}/current_facts.json", "w") as f:
    json.dump(result, f, indent=2)
    f.write("\n")
PYEOF
