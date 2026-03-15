#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

python3 -c "
import json

def to_min(t):
    h, m = map(int, t.split(':'))
    return h * 60 + m

def to_time(m):
    return f'{m // 60:02d}:{m % 60:02d}'

with open('$WORKSPACE/calendar.json') as f:
    data = json.load(f)

busy = sorted([(to_min(m['start_time']), to_min(m['end_time'])) for m in data['meetings']])

slots = []
cursor = to_min('09:00')
end_of_day = to_min('17:00')

for bs, be in busy:
    while cursor + 30 <= bs:
        slots.append({'start_time': to_time(cursor), 'end_time': to_time(cursor + 30), 'duration_minutes': 30})
        cursor += 30
    cursor = max(cursor, be)

while cursor + 30 <= end_of_day:
    slots.append({'start_time': to_time(cursor), 'end_time': to_time(cursor + 30), 'duration_minutes': 30})
    cursor += 30

with open('$WORKSPACE/free_slots.json', 'w') as f:
    json.dump({'date': '2026-03-20', 'slots': slots}, f, indent=2)
"

echo "Solution written to $WORKSPACE/free_slots.json"
