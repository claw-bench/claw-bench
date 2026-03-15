#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

python - "$WORKSPACE" << 'PYEOF'
import sys, json
ws = sys.argv[1]

# Load events
events = []
with open(f"{ws}/events.jsonl") as f:
    for line in f:
        line = line.strip()
        if line:
            events.append(json.loads(line))

# Load rules
with open(f"{ws}/routing_rules.json") as f:
    rules = json.load(f)

def matches_rule(event, rule):
    match = rule["match"]
    for key, expected in match.items():
        actual = event.get(key)
        if isinstance(expected, list):
            if actual not in expected:
                return False
        else:
            if actual != expected:
                return False
    return True

# Process events
with open(f"{ws}/dispatch_log.jsonl", "w") as f:
    for event in events:
        matched_rules = []
        channels = set()
        for rule in rules:
            if matches_rule(event, rule):
                matched_rules.append(rule["name"])
                channels.update(rule["channels"])
        entry = {
            "event_id": event["id"],
            "matched_rules": matched_rules,
            "channels": sorted(channels)
        }
        f.write(json.dumps(entry) + "\n")
PYEOF
