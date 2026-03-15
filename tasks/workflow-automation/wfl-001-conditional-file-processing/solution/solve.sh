#!/usr/bin/env bash
# Oracle solution for wfl-001-conditional-file-processing
set -euo pipefail

WORKSPACE="${1:-workspace}"

python3 -c "
import json

with open('$WORKSPACE/config.json') as f:
    config = json.load(f)

mode = config['mode']

with open('$WORKSPACE/input.txt') as f:
    text = f.read()

if mode == 'uppercase':
    result = text.upper()
elif mode == 'lowercase':
    result = text.lower()
elif mode == 'reverse':
    lines = text.rstrip('\n').split('\n')
    lines.reverse()
    result = '\n'.join(lines) + '\n'
else:
    raise ValueError(f'Unknown mode: {mode}')

with open('$WORKSPACE/output.txt', 'w') as f:
    f.write(result)
"

echo "Solution written to $WORKSPACE/output.txt"
