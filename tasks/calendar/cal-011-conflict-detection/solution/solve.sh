#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

python3 -c "
import json
from collections import defaultdict

def to_min(t):
    h, m = map(int, t.split(':'))
    return h * 60 + m

def to_time(m):
    return f'{m // 60:02d}:{m % 60:02d}'

with open('$WORKSPACE/calendar.json') as f:
    data = json.load(f)

by_date = defaultdict(list)
for m in data['meetings']:
    by_date[m['date']].append(m)

conflicts = []
for date, meetings in sorted(by_date.items()):
    meetings.sort(key=lambda x: (x['start_time'], x['id']))
    for i in range(len(meetings)):
        for j in range(i + 1, len(meetings)):
            a, b = meetings[i], meetings[j]
            a_start, a_end = to_min(a['start_time']), to_min(a['end_time'])
            b_start, b_end = to_min(b['start_time']), to_min(b['end_time'])
            overlap_start = max(a_start, b_start)
            overlap_end = min(a_end, b_end)
            if overlap_start < overlap_end:
                ma, mb = (a, b) if a['start_time'] < b['start_time'] or (a['start_time'] == b['start_time'] and a['id'] < b['id']) else (b, a)
                conflicts.append({
                    'meeting_a': ma['id'],
                    'meeting_b': mb['id'],
                    'date': date,
                    'overlap_start': to_time(overlap_start),
                    'overlap_end': to_time(overlap_end),
                    'overlap_minutes': overlap_end - overlap_start
                })

conflicts.sort(key=lambda c: (c['date'], c['meeting_a']))

with open('$WORKSPACE/conflicts.json', 'w') as f:
    json.dump({'conflicts': conflicts}, f, indent=2)
"

echo "Solution written to $WORKSPACE/conflicts.json"
