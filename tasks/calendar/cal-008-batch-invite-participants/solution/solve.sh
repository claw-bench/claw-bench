#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

python3 -c "
import json
with open('$WORKSPACE/calendar.json') as f:
    cal = json.load(f)
with open('$WORKSPACE/contacts.json') as f:
    contacts = json.load(f)

emails = [c['email'] for c in contacts['contacts']]

for m in cal['meetings']:
    if 'team' in m.get('tags', []):
        existing = set(m['participants'])
        for email in emails:
            if email not in existing:
                m['participants'].append(email)

with open('$WORKSPACE/updated_calendar.json', 'w') as f:
    json.dump(cal, f, indent=2)
"

echo "Solution written to $WORKSPACE/updated_calendar.json"
