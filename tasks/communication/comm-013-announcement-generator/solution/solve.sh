#!/usr/bin/env bash
# Oracle solution for comm-013-announcement-generator
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
mkdir -p "$WORKSPACE/announcements"

python - "$WORKSPACE" << 'PYEOF'
import json
import os
import sys

ws = sys.argv[1]

with open(f"{ws}/template.txt", 'r') as f:
    template = f.read()

with open(f"{ws}/data.json", 'r') as f:
    recipients = json.load(f)

os.makedirs(f"{ws}/announcements", exist_ok=True)

for recipient in recipients:
    content = template
    for key, value in recipient.items():
        content = content.replace('{' + key + '}', value)

    filename = recipient['name'].lower().replace(' ', '_') + '.txt'
    with open(os.path.join(f"{ws}/announcements", filename), 'w') as f:
        f.write(content)
PYEOF

echo "Solution written to $WORKSPACE/announcements/"
