#!/usr/bin/env bash
# Oracle solution for file-014-file-diff
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

python3 -c "
import difflib

with open('$WORKSPACE/original.txt') as f:
    original = f.readlines()
with open('$WORKSPACE/modified.txt') as f:
    modified = f.readlines()

# Use SequenceMatcher for line-by-line diff
sm = difflib.SequenceMatcher(None, original, modified)
output_lines = []

for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag == 'equal':
        for line in original[i1:i2]:
            output_lines.append('  ' + line.rstrip('\n'))
    elif tag == 'delete':
        for line in original[i1:i2]:
            output_lines.append('- ' + line.rstrip('\n'))
    elif tag == 'insert':
        for line in modified[j1:j2]:
            output_lines.append('+ ' + line.rstrip('\n'))
    elif tag == 'replace':
        for line in original[i1:i2]:
            output_lines.append('- ' + line.rstrip('\n'))
        for line in modified[j1:j2]:
            output_lines.append('+ ' + line.rstrip('\n'))

with open('$WORKSPACE/diff.txt', 'w') as f:
    f.write('\n'.join(output_lines) + '\n')
"

echo "Solution written to $WORKSPACE/diff.txt"
