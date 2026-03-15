#!/usr/bin/env bash
# Oracle solution for wfl-006-event-driven-workflow
set -euo pipefail

WORKSPACE="${1:-workspace}"

python3 -c "
import json
from collections import Counter

with open('$WORKSPACE/events.json') as f:
    events = json.load(f)

with open('$WORKSPACE/rules.json') as f:
    rules = json.load(f)

actions = []
events_with_no_match = 0
rule_trigger_counts = Counter()

for event in events:
    matched = False
    for rule in rules:
        condition = rule['condition']
        if all(event.get(k) == v for k, v in condition.items()):
            actions.append({
                'event_id': event['id'],
                'rule_id': rule['id'],
                'action': rule['action'],
                'rule_name': rule['name']
            })
            rule_trigger_counts[rule['id']] += 1
            matched = True
    if not matched:
        events_with_no_match += 1

most_triggered = rule_trigger_counts.most_common(1)[0][0] if rule_trigger_counts else None

output = {
    'actions': actions,
    'summary': {
        'total_events': len(events),
        'total_actions_triggered': len(actions),
        'events_with_no_match': events_with_no_match,
        'most_triggered_rule': most_triggered
    }
}

with open('$WORKSPACE/actions_log.json', 'w') as f:
    json.dump(output, f, indent=2)
"

echo "Solution written to $WORKSPACE/actions_log.json"
