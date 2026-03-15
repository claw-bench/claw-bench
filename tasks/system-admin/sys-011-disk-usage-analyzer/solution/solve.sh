#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

python - "$WORKSPACE" << 'PYEOF'
import sys
import json

ws = sys.argv[1]

entries = []
with open(f"{ws}/disk_usage.txt") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        parts = line.split("\t")
        size_kb = int(parts[0])
        path = parts[1]
        entries.append({"path": path, "size_kb": size_kb})

total_kb = sum(e["size_kb"] for e in entries)
sorted_entries = sorted(entries, key=lambda x: x["size_kb"], reverse=True)
top_5 = sorted_entries[:5]
dirs_over_1gb = [e for e in sorted_entries if e["size_kb"] >= 1048576]

report = {
    "total_usage_kb": total_kb,
    "top_5_largest": top_5,
    "dirs_over_1gb": dirs_over_1gb,
    "entry_count": len(entries)
}

with open(f"{ws}/disk_report.json", "w") as f:
    json.dump(report, f, indent=2)
PYEOF
