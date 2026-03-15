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

with open('$WORKSPACE/draft_schedule.json') as f:
    draft = json.load(f)
with open('$WORKSPACE/preferences.json') as f:
    prefs = json.load(f)

meetings = draft['meetings']
biz_start = to_min(prefs['business_hours']['start'])
biz_end = to_min(prefs['business_hours']['end'])
gap_min = prefs['min_gap_after_long_meetings_minutes']
long_thresh = prefs['long_meeting_threshold_minutes']

days = ['2026-03-16', '2026-03-17', '2026-03-18', '2026-03-19', '2026-03-20']

# Track placed meetings: day -> list of (start, end, duration, id)
placed_by_day = defaultdict(list)
result = []
meeting_durations = {}  # id -> duration

def can_place(day, start, duration):
    end = start + duration
    if start < biz_start or end > biz_end:
        return False
    for ps, pe, pdur, pid in placed_by_day[day]:
        # No overlap
        if start < pe and end > ps:
            return False
        # Gap after long existing meetings
        if pdur > long_thresh and start >= pe and start < pe + gap_min:
            return False
        # Gap after this meeting if it's long, before next existing
        if duration > long_thresh and ps >= end and ps < end + gap_min:
            return False
    return True

def find_slot(day, duration):
    # Collect candidate start times
    candidates = set([biz_start])
    for ps, pe, pdur, pid in placed_by_day[day]:
        candidates.add(pe)
        if pdur > long_thresh:
            candidates.add(pe + gap_min)
    candidates = sorted(candidates)
    for start in candidates:
        if can_place(day, start, duration):
            return start
    return None

def place_meeting(m, day, start):
    entry = dict(m)
    entry['date'] = day
    entry['start_time'] = to_time(start)
    entry['end_time'] = to_time(start + m['duration_minutes'])
    result.append(entry)
    placed_by_day[day].append((start, start + m['duration_minutes'], m['duration_minutes'], m['id']))
    meeting_durations[m['id']] = m['duration_minutes']

# Separate fixed and flexible
fixed = [m for m in meetings if m.get('fixed')]
flexible = [m for m in meetings if not m.get('fixed')]

# Place fixed meetings first
for m in fixed:
    s = to_min(m['start_time'])
    place_meeting(m, m['date'], s)

placed_ids = {m['id'] for m in fixed}

# Sort flexible: preferred day first, longer duration first
flexible.sort(key=lambda m: (0 if m.get('preferred_day') else 1, -m['duration_minutes']))

# First pass: place meetings with preferred days
for m in flexible:
    if m['id'] in placed_ids:
        continue
    if m.get('preferred_day'):
        day = m['preferred_day']
        slot = find_slot(day, m['duration_minutes'])
        if slot is not None:
            place_meeting(m, day, slot)
            placed_ids.add(m['id'])

# Second pass: group remaining by topic and try to place on same day
topics = defaultdict(list)
for m in flexible:
    if m['id'] not in placed_ids:
        topics[m['topic']].append(m)

for topic, group in sorted(topics.items()):
    group.sort(key=lambda x: -x['duration_minutes'])
    placed_group = False
    for day in days:
        # Try to fit all on this day using temporary state
        temp_placed = list(placed_by_day[day])
        temp_slots = []
        all_fit = True
        for gm in group:
            # Find slot considering temp state
            candidates = set([biz_start])
            for ps, pe, pdur, pid in temp_placed:
                candidates.add(pe)
                if pdur > long_thresh:
                    candidates.add(pe + gap_min)
            found = None
            for start in sorted(candidates):
                end = start + gm['duration_minutes']
                if start < biz_start or end > biz_end:
                    continue
                ok = True
                for ps, pe, pdur, pid in temp_placed:
                    if start < pe and end > ps:
                        ok = False
                        break
                    if pdur > long_thresh and start >= pe and start < pe + gap_min:
                        ok = False
                        break
                    if gm['duration_minutes'] > long_thresh and ps >= end and ps < end + gap_min:
                        ok = False
                        break
                if ok:
                    found = start
                    break
            if found is not None:
                temp_slots.append((gm, found))
                temp_placed.append((found, found + gm['duration_minutes'], gm['duration_minutes'], gm['id']))
            else:
                all_fit = False
                break
        if all_fit and len(temp_slots) == len(group):
            for gm, slot in temp_slots:
                place_meeting(gm, day, slot)
                placed_ids.add(gm['id'])
            placed_group = True
            break

    if not placed_group:
        for gm in group:
            if gm['id'] in placed_ids:
                continue
            for day in days:
                slot = find_slot(day, gm['duration_minutes'])
                if slot is not None:
                    place_meeting(gm, day, slot)
                    placed_ids.add(gm['id'])
                    break

with open('$WORKSPACE/optimized_schedule.json', 'w') as f:
    json.dump({'meetings': result}, f, indent=2)
"

echo "Solution written to $WORKSPACE/optimized_schedule.json"
