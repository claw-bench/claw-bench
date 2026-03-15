#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

python3 -c "
import json
from collections import defaultdict

with open('$WORKSPACE/calendar.json') as f:
    data = json.load(f)

meetings = data['meetings']
durations = [m['duration_minutes'] for m in meetings]
total_min = sum(durations)

day_hours = defaultdict(float)
for m in meetings:
    day_hours[m['date']] += m['duration_minutes'] / 60.0

busiest = min(day_hours.items(), key=lambda x: (-x[1], x[0]))

stats = {
    'total_meetings': len(meetings),
    'total_hours': total_min / 60.0,
    'average_duration_minutes': round(total_min / len(meetings), 1),
    'busiest_day': busiest[0],
    'busiest_day_hours': busiest[1],
    'shortest_meeting_minutes': min(durations),
    'longest_meeting_minutes': max(durations)
}

with open('$WORKSPACE/calendar_stats.json', 'w') as f:
    json.dump(stats, f, indent=2)
"

echo "Solution written to $WORKSPACE/calendar_stats.json"
