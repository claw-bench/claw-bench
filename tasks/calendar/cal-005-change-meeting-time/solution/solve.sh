#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

python3 -c "
import json
with open('$WORKSPACE/calendar.json') as f:
    data = json.load(f)
for m in data['meetings']:
    if m['id'] == 'mtg-001':
        m['date'] = '2026-03-20'
        m['start_time'] = '14:00'
with open('$WORKSPACE/updated_calendar.json', 'w') as f:
    json.dump(data, f, indent=2)
"

echo "Solution written to $WORKSPACE/updated_calendar.json"
