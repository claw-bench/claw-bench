#!/usr/bin/env bash
# Oracle solution for sys-007-service-dependency-mapping
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

python3 -c "
import json
try:
    import yaml
except ImportError:
    # Fallback: simple YAML parser for this specific format
    import re

    def parse_yaml(path):
        services = {}
        current_service = None
        with open(path) as f:
            for line in f:
                line = line.rstrip()
                if not line or line.startswith('services:'):
                    continue
                # Service name (2 spaces indent)
                m = re.match(r'^  (\w+):$', line)
                if m:
                    current_service = m.group(1)
                    services[current_service] = {'description': '', 'depends_on': []}
                    continue
                if current_service:
                    m = re.match(r'^    description: \"(.+)\"$', line)
                    if m:
                        services[current_service]['description'] = m.group(1)
                        continue
                    if 'depends_on: []' in line:
                        continue
                    if 'depends_on:' in line and '[]' not in line:
                        continue
                    m = re.match(r'^      - (\w+)$', line)
                    if m:
                        services[current_service]['depends_on'].append(m.group(1))
        return {'services': services}

    yaml = type('', (), {'safe_load': None})()

with open('$WORKSPACE/services.yaml') as f:
    content = f.read()

try:
    import yaml as y
    data = y.safe_load(content)
except:
    data = parse_yaml('$WORKSPACE/services.yaml')

services = data['services']

# Topological sort using Kahn's algorithm
in_degree = {s: 0 for s in services}
graph = {s: [] for s in services}
for name, svc in services.items():
    deps = svc.get('depends_on', []) or []
    in_degree[name] = len(deps)
    for dep in deps:
        graph[dep].append(name)

queue = [s for s in services if in_degree[s] == 0]
queue.sort()
order = []
while queue:
    node = queue.pop(0)
    order.append(node)
    for neighbor in sorted(graph[node]):
        in_degree[neighbor] -= 1
        if in_degree[neighbor] == 0:
            queue.append(neighbor)
    queue.sort()

# Calculate dependency levels
levels = {}
for name in services:
    deps = services[name].get('depends_on', []) or []
    if not deps:
        levels[name] = 0
    else:
        levels[name] = -1  # unresolved

changed = True
while changed:
    changed = False
    for name in services:
        if levels[name] >= 0:
            continue
        deps = services[name].get('depends_on', []) or []
        if all(levels.get(d, -1) >= 0 for d in deps):
            levels[name] = max(levels[d] for d in deps) + 1
            changed = True

max_level = max(levels.values())
dep_levels = []
for lvl in range(max_level + 1):
    svcs = sorted([s for s, l in levels.items() if l == lvl])
    dep_levels.append({'level': lvl, 'services': svcs})

svc_info = {}
for name, svc in services.items():
    svc_info[name] = {
        'depends_on': svc.get('depends_on', []) or [],
        'description': svc.get('description', '')
    }

report = {
    'services': svc_info,
    'startup_order': order,
    'dependency_levels': dep_levels,
    'total_services': len(services)
}

with open('$WORKSPACE/dependency_order.json', 'w') as f:
    json.dump(report, f, indent=2)
"

echo "Solution written to $WORKSPACE/dependency_order.json"
