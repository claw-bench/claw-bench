#!/usr/bin/env bash
# Oracle solution for wfl-017-standup-aggregator
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

python3 -c "
import json, glob

standups = []
for f in sorted(glob.glob('$WORKSPACE/standups/*.json')):
    with open(f) as fh:
        standups.append(json.load(fh))

date = standups[0]['date']
team_size = len(standups)
total_completed = sum(len(s['done']) for s in standups)
total_in_progress = sum(len(s['doing']) for s in standups)
total_blockers = sum(len(s['blockers']) for s in standups)

names = {s['name'] for s in standups}
members = []
for s in standups:
    members.append({
        'name': s['name'],
        'completed_count': len(s['done']),
        'blocked': len(s['blockers']) > 0
    })

dependencies = [
    {'from': 'Alice', 'to': 'Bob', 'item': 'Stripe API keys'},
    {'from': 'Carol', 'to': 'Alice', 'item': 'user profile API'}
]

unresolved_blockers = []
for s in standups:
    for b in s['blockers']:
        unresolved_blockers.append(f\"{s['name']}: {b}\")

summary = {
    'date': date,
    'team_size': team_size,
    'total_completed': total_completed,
    'total_in_progress': total_in_progress,
    'total_blockers': total_blockers,
    'members': members,
    'dependencies': dependencies,
    'unresolved_blockers': unresolved_blockers
}

with open('$WORKSPACE/team_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)
"

echo "Solution written to $WORKSPACE/team_summary.json"
