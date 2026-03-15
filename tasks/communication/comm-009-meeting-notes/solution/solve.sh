#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
mkdir -p "$WORKSPACE"

python - "$WORKSPACE" << 'PYEOF'
import sys
import json

ws = sys.argv[1]

notes = {
    'meeting_title': 'Q3 Product Launch Planning Meeting',
    'date': '2025-01-15',
    'attendees': [
        'Sarah Chen',
        "James O'Brien",
        'Priya Patel',
        'Marcus Williams',
        'Lisa Yamamoto'
    ],
    'action_items': [
        {
            'owner': "James O'Brien",
            'task': 'Prepare the final feature specification document',
            'deadline': '2025-02-28'
        },
        {
            'owner': 'Marcus Williams',
            'task': 'Draft the product positioning document',
            'deadline': '2025-03-15'
        },
        {
            'owner': 'Marcus Williams',
            'task': 'Finalize the product positioning document with Lisa',
            'deadline': '2025-04-01'
        },
        {
            'owner': 'Priya Patel',
            'task': 'Prepare the beta testing plan',
            'deadline': '2025-03-31'
        },
        {
            'owner': 'Priya Patel',
            'task': 'Recruit beta testers',
            'deadline': '2025-04-15'
        },
        {
            'owner': "James O'Brien",
            'task': 'Redesign the signup UX mockups for freemium model',
            'deadline': '2025-03-01'
        },
        {
            'owner': 'Lisa Yamamoto',
            'task': 'Prepare detailed marketing budget breakdown',
            'deadline': '2025-02-15'
        }
    ],
    'decisions': [
        'Launch date set for July 15, 2025',
        'Beta testing phase extended to six weeks (May 1 - June 12)',
        'CloudSync Pro will use a freemium pricing model',
        'Launch marketing budget set at $150,000'
    ],
    'next_meeting': '2025-01-29'
}

with open(f'{ws}/notes.json', 'w') as f:
    json.dump(notes, f, indent=2)
PYEOF

echo "Solution written to $WORKSPACE/notes.json"
