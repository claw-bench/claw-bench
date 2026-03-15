#!/usr/bin/env bash
# Oracle solution for wfl-009-scheduled-workflow-plan
set -euo pipefail

WORKSPACE="${1:-workspace}"

python3 -c "
import json
from collections import defaultdict, deque

with open('$WORKSPACE/tasks.json') as f:
    tasks = json.load(f)

task_map = {t['id']: t for t in tasks}

# Topological sort using Kahn's algorithm
in_degree = {t['id']: len(t['dependencies']) for t in tasks}
adj = defaultdict(list)
for t in tasks:
    for dep in t['dependencies']:
        adj[dep].append(t['id'])

queue = deque([tid for tid, deg in in_degree.items() if deg == 0])
topo_order = []
while queue:
    tid = queue.popleft()
    topo_order.append(tid)
    for nxt in adj[tid]:
        in_degree[nxt] -= 1
        if in_degree[nxt] == 0:
            queue.append(nxt)

# Forward pass: earliest start/finish
earliest_start = {}
earliest_finish = {}
for tid in topo_order:
    t = task_map[tid]
    if not t['dependencies']:
        earliest_start[tid] = 0
    else:
        earliest_start[tid] = max(earliest_finish[d] for d in t['dependencies'])
    earliest_finish[tid] = earliest_start[tid] + t['duration']

total_duration = max(earliest_finish.values())

# Backward pass: latest start/finish
latest_finish_map = {}
latest_start = {}
for tid in reversed(topo_order):
    successors = adj[tid]
    if not successors:
        latest_finish_map[tid] = total_duration
    else:
        latest_finish_map[tid] = min(latest_start[s] for s in successors)
    latest_start[tid] = latest_finish_map[tid] - task_map[tid]['duration']

# Build schedule
schedule_tasks = []
for tid in topo_order:
    t = task_map[tid]
    slack = latest_start[tid] - earliest_start[tid]
    schedule_tasks.append({
        'id': tid,
        'name': t['name'],
        'duration': t['duration'],
        'earliest_start': earliest_start[tid],
        'earliest_finish': earliest_finish[tid],
        'latest_start': latest_start[tid],
        'latest_finish': latest_finish_map[tid],
        'slack': slack
    })

schedule = {
    'tasks': schedule_tasks,
    'total_duration': total_duration
}

with open('$WORKSPACE/schedule.json', 'w') as f:
    json.dump(schedule, f, indent=2)

# Critical path: tasks with 0 slack, in topological order
critical_tasks = [t for t in schedule_tasks if t['slack'] == 0]
critical_path = {
    'path': [t['id'] for t in critical_tasks],
    'total_duration': total_duration,
    'path_length': len(critical_tasks)
}

with open('$WORKSPACE/critical_path.json', 'w') as f:
    json.dump(critical_path, f, indent=2)
"

echo "Solution written to $WORKSPACE/schedule.json and $WORKSPACE/critical_path.json"
