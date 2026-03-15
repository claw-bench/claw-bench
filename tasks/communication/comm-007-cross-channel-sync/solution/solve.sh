#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${1:-workspace}"

python3 -c "
import json

with open('$WORKSPACE/channels.json') as f:
    channels = {c['id']: c for c in json.load(f)}
with open('$WORKSPACE/sync_rules.json') as f:
    rules = json.load(f)

sync_pairs = []
warnings = []
edges = {}  # for cycle detection

for rule in rules:
    src = rule['source_channel']
    tgt = rule['target_channel']
    src_types = set(channels[src]['content_types'])
    tgt_types = set(channels[tgt]['content_types'])

    directions = [(src, tgt)]
    if rule['direction'] == 'two-way':
        directions.append((tgt, src))

    for s, t in directions:
        s_types = set(channels[s]['content_types'])
        t_types = set(channels[t]['content_types'])
        valid = []
        for ct in rule['content_types']:
            if ct not in s_types:
                warnings.append(f\"Content type '{ct}' not supported by source channel '{s}'\")
            elif ct not in t_types:
                warnings.append(f\"Content type '{ct}' not supported by target channel '{t}'\")
            else:
                valid.append(ct)
        if valid:
            sync_pairs.append({
                'source': s,
                'target': t,
                'content_types': valid,
                'direction': 'one-way'
            })
            edges.setdefault(s, []).append(t)

# Cycle detection using DFS
def find_cycles(graph):
    cycles = []
    visited = set()
    rec_stack = set()
    path = []

    def dfs(node):
        visited.add(node)
        rec_stack.add(node)
        path.append(node)
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                dfs(neighbor)
            elif neighbor in rec_stack:
                idx = path.index(neighbor)
                cycle = path[idx:] + [neighbor]
                cycles.append(cycle)
        path.pop()
        rec_stack.discard(node)

    for node in graph:
        if node not in visited:
            dfs(node)
    return cycles

cycles = find_cycles(edges)
for cycle in cycles:
    warnings.append(f\"Circular sync detected: {' -> '.join(cycle)}\")

# Channel summary
channel_summary = {}
for cid in channels:
    channel_summary[cid] = {'syncs_to': [], 'syncs_from': []}
for pair in sync_pairs:
    channel_summary[pair['source']]['syncs_to'].append(pair['target'])
    channel_summary[pair['target']]['syncs_from'].append(pair['source'])

result = {
    'sync_pairs': sync_pairs,
    'warnings': warnings,
    'channel_summary': channel_summary
}

with open('$WORKSPACE/sync_plan.json', 'w') as f:
    json.dump(result, f, indent=2)
"

echo "Solution written to $WORKSPACE/sync_plan.json"
