#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

python3 -c "
import json
with open('$WORKSPACE/calendar.json') as f:
    data = json.load(f)
today = [e for e in data['events'] if e['date'] == '2026-03-15']
today.sort(key=lambda e: e['start_time'])
with open('$WORKSPACE/today.json', 'w') as f:
    json.dump({'events': today}, f, indent=2)
"

echo "Solution written to $WORKSPACE/today.json"
