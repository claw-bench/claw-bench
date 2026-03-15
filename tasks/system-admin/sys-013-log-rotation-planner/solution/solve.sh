#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

python - "$WORKSPACE" << 'PYEOF'
import sys
import json
from datetime import datetime

ws = sys.argv[1]

reference_date = datetime(2025, 3, 1)

with open(f"{ws}/log_inventory.json") as f:
    inventory = json.load(f)

files = []
rotate_count = 0
compress_count = 0
delete_count = 0
no_action_count = 0

for entry in inventory:
    last_mod = datetime.strptime(entry["last_modified"], "%Y-%m-%d")
    age_days = (reference_date - last_mod).days
    retention = entry["retention_days"]
    size = entry["size_mb"]

    actions = []

    should_rotate = size >= 100 or age_days > retention
    if should_rotate:
        actions.append("rotate")

    if should_rotate and size >= 50:
        actions.append("compress")

    if age_days > retention * 2:
        actions.append("delete")

    if not actions:
        no_action_count += 1
    if "rotate" in actions:
        rotate_count += 1
    if "compress" in actions:
        compress_count += 1
    if "delete" in actions:
        delete_count += 1

    files.append({
        "path": entry["path"],
        "size_mb": size,
        "age_days": age_days,
        "retention_days": retention,
        "actions": actions
    })

plan = {
    "reference_date": "2025-03-01",
    "files": files,
    "summary": {
        "total_files": len(files),
        "files_to_rotate": rotate_count,
        "files_to_compress": compress_count,
        "files_to_delete": delete_count,
        "files_no_action": no_action_count
    }
}

with open(f"{ws}/rotation_plan.json", "w") as f:
    json.dump(plan, f, indent=2)
PYEOF
