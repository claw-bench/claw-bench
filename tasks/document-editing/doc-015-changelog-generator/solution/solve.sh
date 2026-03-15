#!/usr/bin/env bash
# Oracle solution for doc-015-changelog-generator
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
mkdir -p "$WORKSPACE"

python - "$WORKSPACE" << 'PYEOF'
import json
import sys
from collections import OrderedDict

ws = sys.argv[1]

type_headings = OrderedDict([
    ('feat', 'Features'),
    ('fix', 'Bug Fixes'),
    ('docs', 'Documentation'),
    ('chore', 'Chores'),
])

groups = {t: [] for t in type_headings}

with open(f'{ws}/commits.jsonl', 'r') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        commit = json.loads(line)
        ctype = commit['type']
        if ctype in groups:
            groups[ctype].append(commit)

lines = ['# Changelog', '']

for ctype, heading in type_headings.items():
    if groups[ctype]:
        lines.append(f'## {heading}')
        for c in groups[ctype]:
            lines.append(f"- {c['message']} ({c['hash']}) - {c['author']}")
        lines.append('')

with open(f'{ws}/CHANGELOG.md', 'w') as f:
    f.write('\n'.join(lines))
PYEOF

echo "Solution written to $WORKSPACE/CHANGELOG.md"
