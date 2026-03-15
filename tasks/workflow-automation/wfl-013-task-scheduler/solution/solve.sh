#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

python - "$WORKSPACE" << 'PYEOF'
import sys, json
ws = sys.argv[1]

with open(f"{ws}/tasks.json") as f:
    tasks = json.load(f)

task_map = {t["id"]: t for t in tasks}
scheduled = []
completed = {}  # id -> end_time
remaining = set(t["id"] for t in tasks)
current_time = 0

while remaining:
    # Find ready tasks (all deps completed)
    ready = []
    for tid in remaining:
        t = task_map[tid]
        if all(d in completed for d in t["dependencies"]):
            earliest_start = max([completed[d] for d in t["dependencies"]], default=0)
            ready.append((tid, earliest_start))

    if not ready:
        break

    # Sort by: priority (asc), deadline (asc)
    ready.sort(key=lambda x: (task_map[x[0]]["priority"], task_map[x[0]]["deadline"]))

    tid, earliest = ready[0]
    t = task_map[tid]
    start = max(current_time, earliest)
    end = start + t["duration_minutes"]

    scheduled.append({
        "id": tid,
        "start_time": start,
        "end_time": end
    })
    completed[tid] = end
    current_time = end
    remaining.remove(tid)

with open(f"{ws}/schedule.json", "w") as f:
    json.dump(scheduled, f, indent=2)
PYEOF
