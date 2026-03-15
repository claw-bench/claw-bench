#!/usr/bin/env bash
# Oracle solution for doc-012-text-find-replace
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
mkdir -p "$WORKSPACE"

python - "$WORKSPACE" << 'PYEOF'
import json
import sys

ws = sys.argv[1]

with open(f'{ws}/document.txt', 'r') as f:
    text = f.read()

with open(f'{ws}/replacements.json', 'r') as f:
    replacements = json.load(f)

for pair in replacements:
    text = text.replace(pair['find'], pair['replace'])

with open(f'{ws}/output.txt', 'w') as f:
    f.write(text)
PYEOF

echo "Solution written to $WORKSPACE/output.txt"
