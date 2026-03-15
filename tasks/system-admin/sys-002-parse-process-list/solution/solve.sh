#!/usr/bin/env bash
# Oracle solution for sys-002-parse-process-list
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

python3 -c "
import json

processes = []
with open('$WORKSPACE/processes.txt') as f:
    header = f.readline()  # skip header
    for line in f:
        line = line.strip()
        if not line:
            continue
        parts = line.split(None, 10)
        proc = {
            'user': parts[0],
            'pid': int(parts[1]),
            'cpu_percent': float(parts[2]),
            'mem_percent': float(parts[3]),
            'command': parts[10]
        }
        processes.append(proc)

total_cpu = sum(p['cpu_percent'] for p in processes)
total_mem = sum(p['mem_percent'] for p in processes)
sorted_procs = sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)
top5 = sorted_procs[:5]

report = {
    'total_processes': len(processes),
    'top_5_cpu': [
        {
            'pid': p['pid'],
            'user': p['user'],
            'cpu_percent': p['cpu_percent'],
            'mem_percent': p['mem_percent'],
            'command': p['command']
        }
        for p in top5
    ],
    'total_cpu_usage': round(total_cpu, 1),
    'total_mem_usage': round(total_mem, 1)
}

with open('$WORKSPACE/top_processes.json', 'w') as f:
    json.dump(report, f, indent=2)
"

echo "Solution written to $WORKSPACE/top_processes.json"
