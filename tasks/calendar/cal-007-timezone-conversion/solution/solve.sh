#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

python3 -c "
import json
from datetime import datetime, timedelta

with open('$WORKSPACE/calendar.json') as f:
    data = json.load(f)

for m in data['meetings']:
    date = datetime.strptime(m['date'], '%Y-%m-%d')
    sh, sm = map(int, m['start_time'].split(':'))
    eh, em = map(int, m['end_time'].split(':'))

    start_dt = date.replace(hour=sh, minute=sm) - timedelta(hours=7)
    end_dt = date.replace(hour=eh, minute=em) - timedelta(hours=7)

    m['date'] = start_dt.strftime('%Y-%m-%d')
    m['start_time'] = start_dt.strftime('%H:%M')
    m['end_time'] = end_dt.strftime('%H:%M')
    m['timezone'] = 'US/Pacific'

data['timezone'] = 'US/Pacific'
with open('$WORKSPACE/converted_calendar.json', 'w') as f:
    json.dump(data, f, indent=2)
"

echo "Solution written to $WORKSPACE/converted_calendar.json"
