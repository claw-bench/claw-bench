#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

python - "$WORKSPACE" << 'PYEOF'
import sys
import json
from collections import deque

ws = sys.argv[1]

with open(f"{ws}/services.json") as f:
    services = json.load(f)

# Build adjacency list and in-degree map
graph = {}
in_degree = {}
all_names = set()

for svc in services:
    name = svc["name"]
    all_names.add(name)
    if name not in graph:
        graph[name] = []
    if name not in in_degree:
        in_degree[name] = 0
    for dep in svc["depends_on"]:
        all_names.add(dep)
        if dep not in graph:
            graph[dep] = []
        if dep not in in_degree:
            in_degree[dep] = 0
        graph[dep].append(name)
        in_degree[name] += 1

# Kahn's algorithm for topological sort
queue = deque()
for name in sorted(all_names):
    if in_degree[name] == 0:
        queue.append(name)

startup_order = []
while queue:
    # Sort to get deterministic order among nodes with same in-degree
    queue_list = sorted(queue)
    queue.clear()
    for node in queue_list:
        startup_order.append(node)
        for neighbor in sorted(graph.get(node, [])):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

# Check for cycles
has_cycle = len(startup_order) < len(all_names)
circular = []
if has_cycle:
    circular = sorted([n for n in all_names if n not in startup_order])

result = {
    "startup_order": startup_order,
    "has_circular_dependency": has_cycle,
    "circular_dependencies": circular,
    "total_services": len(all_names)
}

with open(f"{ws}/startup_order.json", "w") as f:
    json.dump(result, f, indent=2)
PYEOF
