#!/usr/bin/env bash
# Oracle solution for eml-015-auto-reply-generator
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

python - "$WORKSPACE" << 'PYEOF'
import json, sys
import yaml

ws = sys.argv[1]

with open(f'{ws}/inbox.json') as f:
    inbox = json.load(f)

with open(f'{ws}/rules.yaml') as f:
    config = yaml.safe_load(f)

rules = config['rules']

auto_replies = []

for email in inbox:
    subject_lower = email['subject'].lower()
    for rule in rules:
        pattern = rule['subject_pattern'].lower()
        if pattern in subject_lower:
            reply_body = rule['reply_template'].replace(
                '{sender}', email['from']
            ).replace(
                '{subject}', email['subject']
            ).replace(
                '{date}', email['date']
            )
            auto_replies.append({
                'original_id': email['id'],
                'from': email['from'],
                'subject': email['subject'],
                'matched_rule': rule['subject_pattern'],
                'reply_body': reply_body
            })
            break

with open(f'{ws}/auto_replies.json', 'w') as f:
    json.dump(auto_replies, f, indent=2)
PYEOF

echo "Auto-replies generated to $WORKSPACE/auto_replies.json"
