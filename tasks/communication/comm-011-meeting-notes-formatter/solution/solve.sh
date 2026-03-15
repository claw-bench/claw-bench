#!/usr/bin/env bash
# Oracle solution for comm-011-meeting-notes-formatter
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
mkdir -p "$WORKSPACE"

python - "$WORKSPACE" << 'PYEOF'
import json
import re
import sys

ws = sys.argv[1]

with open(f"{ws}/meeting.txt", 'r') as f:
    lines = f.readlines()

attendees = set()
action_items = []
decisions = []

for line in lines:
    line = line.strip()
    # Extract speaker: pattern is [timestamp] Name: text
    match = re.match(r'\[\d{2}:\d{2}\]\s+(\w+):', line)
    if match:
        attendees.add(match.group(1))

    # Extract action items
    if 'ACTION:' in line:
        action_text = line.split('ACTION:')[1].strip()
        action_items.append(action_text)

    # Extract decisions
    if 'DECISION:' in line:
        decision_text = line.split('DECISION:')[1].strip()
        decisions.append(decision_text)

result = {
    'attendees': sorted(list(attendees)),
    'action_items': action_items,
    'decisions': decisions
}

with open(f"{ws}/meeting_notes.json", 'w') as f:
    json.dump(result, f, indent=2)
PYEOF

echo "Solution written to $WORKSPACE/meeting_notes.json"
