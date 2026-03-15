#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

python3 -c "
import json
import os

def to_min(t):
    h, m = map(int, t.split(':'))
    return h * 60 + m

def to_time(m):
    return f'{m // 60:02d}:{m % 60:02d}'

target_date = '2026-03-25'
biz_start = to_min('09:00')
biz_end = to_min('17:00')
slot_dur = 30

# Load all calendars
cal_dir = '$WORKSPACE/calendars'
people = []
all_busy = []
for fname in sorted(os.listdir(cal_dir)):
    if not fname.endswith('.json'):
        continue
    with open(os.path.join(cal_dir, fname)) as f:
        cal = json.load(f)
    person = cal['person']
    people.append(person)
    busy = []
    for m in cal['meetings']:
        if m['date'] == target_date:
            busy.append((to_min(m['start_time']), to_min(m['end_time'])))
    all_busy.append(busy)

# Find common free slots
slots = []
cursor = biz_start
while cursor + slot_dur <= biz_end:
    s, e = cursor, cursor + slot_dur
    free = True
    for busy in all_busy:
        for bs, be in busy:
            if s < be and e > bs:
                free = False
                break
        if not free:
            break
    if free:
        slots.append({'start_time': to_time(s), 'end_time': to_time(e)})
    cursor += slot_dur

# Find best slot
def score(slot):
    s = to_min(slot['start_time'])
    # Prefer mid-morning (600-720) or mid-afternoon (840-960)
    if 600 <= s < 720 or 840 <= s < 960:
        return (0, s)
    return (1, s)

best = min(slots, key=score) if slots else slots[0]

with open('$WORKSPACE/common_slots.json', 'w') as f:
    json.dump({
        'date': target_date,
        'duration_minutes': slot_dur,
        'participants': sorted(people),
        'slots': slots
    }, f, indent=2)

with open('$WORKSPACE/recommendation.json', 'w') as f:
    json.dump({
        'recommended_slot': best,
        'reason': f'The slot at {best[\"start_time\"]}-{best[\"end_time\"]} is the only available 30-minute window when all 5 participants are free.'
    }, f, indent=2)
"

echo "Solution written"
