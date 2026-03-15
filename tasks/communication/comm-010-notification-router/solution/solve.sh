#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
mkdir -p "$WORKSPACE"

python - "$WORKSPACE" << 'PYEOF'
import json
import sys

ws = sys.argv[1]

# Parse YAML manually to avoid requiring pyyaml
# Simple YAML parser for this specific structure
def parse_rules_yaml(path):
    with open(path) as f:
        lines = f.readlines()

    rules = []
    current_rule = None
    in_conditions = False
    current_key = None

    for line in lines:
        stripped = line.rstrip()
        if not stripped or stripped.startswith('#'):
            continue

        indent = len(line) - len(line.lstrip())

        if '- name:' in stripped:
            if current_rule:
                rules.append(current_rule)
            name = stripped.split('name:')[1].strip().strip('"').strip("'")
            current_rule = {'name': name, 'conditions': {}, 'channels': [], 'priority': 'default'}
            in_conditions = False
            continue

        if current_rule is None:
            continue

        if 'conditions:' in stripped and ':' == stripped.strip().split('conditions')[1][0]:
            in_conditions = True
            continue

        if 'channels:' in stripped:
            in_conditions = False
            # Parse inline array
            arr_str = stripped.split('channels:')[1].strip()
            if arr_str.startswith('['):
                items = arr_str.strip('[]').split(',')
                current_rule['channels'] = [i.strip().strip('"').strip("'") for i in items]
            continue

        if 'priority:' in stripped and indent >= 4:
            in_conditions = False
            current_rule['priority'] = stripped.split('priority:')[1].strip().strip('"').strip("'")
            continue

        if in_conditions and indent >= 6:
            s = stripped.strip()
            if ':' in s:
                key, val = s.split(':', 1)
                key = key.strip()
                val = val.strip()
                if val.startswith('['):
                    items = val.strip('[]').split(',')
                    current_rule['conditions'][key] = [i.strip().strip('"').strip("'") for i in items]
                else:
                    # Try numeric
                    try:
                        current_rule['conditions'][key] = int(val)
                    except ValueError:
                        current_rule['conditions'][key] = val.strip('"').strip("'")

    if current_rule:
        rules.append(current_rule)

    return rules

def matches_rule(event, rule):
    conds = rule['conditions']

    if 'event_type' in conds:
        if event.get('type') != conds['event_type']:
            return False

    if 'severity_gte' in conds:
        if event.get('severity', 0) < conds['severity_gte']:
            return False

    if 'source_in' in conds:
        if event.get('source') not in conds['source_in']:
            return False

    if 'tag_contains' in conds:
        event_tags = set(event.get('tags', []))
        rule_tags = set(conds['tag_contains'])
        if not event_tags.intersection(rule_tags):
            return False

    return True

rules = parse_rules_yaml(f'{ws}/rules.yaml')

with open(f'{ws}/events.json') as f:
    events = json.load(f)

results = []
for event in events:
    matched = None
    for rule in rules:
        if matches_rule(event, rule):
            matched = rule
            break

    if matched:
        results.append({
            'event_id': event['event_id'],
            'matched_rule': matched['name'],
            'channels': matched['channels'],
            'priority': matched['priority']
        })
    else:
        results.append({
            'event_id': event['event_id'],
            'matched_rule': None,
            'channels': ['log'],
            'priority': 'default'
        })

with open(f'{ws}/routed_notifications.json', 'w') as f:
    json.dump(results, f, indent=2)
PYEOF

echo "Solution written to $WORKSPACE/routed_notifications.json"
