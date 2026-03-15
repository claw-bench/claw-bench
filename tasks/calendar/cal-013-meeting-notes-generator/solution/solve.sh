#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

python3 -c "
import json

with open('$WORKSPACE/meeting.json') as f:
    meeting = json.load(f)
with open('$WORKSPACE/attendees.json') as f:
    attendees = json.load(f)['attendees']

lines = []
lines.append('# Meeting Preparation Notes')
lines.append('')
lines.append('## Meeting Overview')
lines.append('')
lines.append(f'- **Title:** {meeting[\"title\"]}')
lines.append(f'- **Date:** {meeting[\"date\"]}')
lines.append(f'- **Time:** {meeting[\"start_time\"]} - {meeting[\"end_time\"]} ({meeting[\"duration_minutes\"]} minutes)')
lines.append(f'- **Location:** {meeting[\"location\"]}')
lines.append(f'- **Organizer:** {meeting[\"organizer\"]}')
lines.append('')
lines.append('## Attendees')
lines.append('')
for a in attendees:
    lines.append(f'- **{a[\"name\"]}** - {a[\"role\"]}, {a[\"department\"]}')
lines.append('')
lines.append('## Agenda')
lines.append('')
for i, item in enumerate(meeting['agenda'], 1):
    lines.append(f'{i}. {item}')
lines.append('')
lines.append('## Previous Action Items')
lines.append('')
for a in attendees:
    open_items = [ai for ai in a['action_items'] if ai['status'] == 'open']
    if open_items:
        lines.append(f'**{a[\"name\"]}:**')
        for ai in open_items:
            lines.append(f'- {ai[\"description\"]}')
        lines.append('')
lines.append('## References')
lines.append('')
for ref in meeting['references']:
    lines.append(f'- {ref[\"title\"]} ({ref[\"date\"]})')

with open('$WORKSPACE/prep_notes.md', 'w') as f:
    f.write('\n'.join(lines) + '\n')
"

echo "Solution written to $WORKSPACE/prep_notes.md"
