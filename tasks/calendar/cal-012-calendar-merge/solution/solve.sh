#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

python3 -c "
import json

def to_min(t):
    h, m = map(int, t.split(':'))
    return h * 60 + m

with open('$WORKSPACE/work_calendar.json') as f:
    work = json.load(f)['events']
with open('$WORKSPACE/personal_calendar.json') as f:
    personal = json.load(f)['events']

merged = list(work)
displaced = []

for p in personal:
    conflicting = None
    for w in sorted(work, key=lambda x: x['start_time']):
        if w['date'] != p['date']:
            continue
        w_s, w_e = to_min(w['start_time']), to_min(w['end_time'])
        p_s, p_e = to_min(p['start_time']), to_min(p['end_time'])
        if p_s < w_e and p_e > w_s:
            conflicting = w['id']
            break
    if conflicting:
        p['displaced_by'] = conflicting
        displaced.append(p)
    else:
        merged.append(p)

merged.sort(key=lambda e: (e['date'], e['start_time']))

with open('$WORKSPACE/merged_calendar.json', 'w') as f:
    json.dump({'events': merged}, f, indent=2)
with open('$WORKSPACE/displaced.json', 'w') as f:
    json.dump({'displaced_events': displaced}, f, indent=2)
"

echo "Solution written"
