#!/usr/bin/env bash
# Oracle solution for mem-010-multi-file-context-correlation
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

python - "$WORKSPACE" << 'PYEOF'
import sys
import os

ws = sys.argv[1]

files = sorted(['file_a.txt', 'file_b.txt', 'file_c.txt', 'file_d.txt', 'file_e.txt'])
words = []

for fname in files:
    path = os.path.join(ws, fname)
    with open(path, 'r') as f:
        content = f.read().strip()
        first_word = content.split()[0]
        words.append(first_word)

message = ' '.join(words)

with open(os.path.join(ws, 'answer.txt'), 'w') as f:
    f.write(message + '\n')

print(f'Hidden message: {message}')
PYEOF

echo "Solution written to $WORKSPACE/answer.txt"
