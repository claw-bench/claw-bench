#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${1:-workspace}"

python3 -c "
import json

with open('$WORKSPACE/messages.json') as f:
    messages = json.load(f)

strings = {}
for msg_id, fields in messages.items():
    for field_name, value in fields.items():
        if isinstance(value, str):
            strings[f'{msg_id}.{field_name}'] = value

result = dict(sorted(strings.items()))
with open('$WORKSPACE/strings.json', 'w') as f:
    json.dump(result, f, indent=2)
"

echo "Solution written to $WORKSPACE/strings.json"
