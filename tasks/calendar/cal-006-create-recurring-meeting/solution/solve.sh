#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

python3 -c "
import json
from datetime import datetime, timedelta

start = datetime(2026, 3, 16)
meetings = []
for i in range(4):
    date = start + timedelta(weeks=i)
    meetings.append({
        'id': f'rec-{i+1:03d}',
        'series_id': 'series-weekly-sync',
        'title': 'Weekly Team Sync',
        'date': date.strftime('%Y-%m-%d'),
        'start_time': '10:00',
        'end_time': '11:00',
        'duration_minutes': 60,
        'participants': ['alice@example.com', 'bob@example.com', 'charlie@example.com'],
        'location': 'Conference Room B'
    })
with open('$WORKSPACE/recurring.json', 'w') as f:
    json.dump({'meetings': meetings}, f, indent=2)
"

echo "Solution written to $WORKSPACE/recurring.json"
