#!/usr/bin/env bash
# Oracle solution for doc-014-document-merger
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
mkdir -p "$WORKSPACE"

python - "$WORKSPACE" << 'PYEOF'
import sys

ws = sys.argv[1]

sections = []
for i in range(1, 5):
    with open(f'{ws}/parts/part{i}.txt', 'r') as f:
        content = f.read()
    lines = content.split('\n', 1)
    title = lines[0].strip()
    body = lines[1] if len(lines) > 1 else ''
    section = f'## Section {i}: {title}\n{body}'
    sections.append(section.rstrip())

with open(f'{ws}/merged.txt', 'w') as f:
    f.write('\n\n'.join(sections) + '\n')
PYEOF

echo "Solution written to $WORKSPACE/merged.txt"
