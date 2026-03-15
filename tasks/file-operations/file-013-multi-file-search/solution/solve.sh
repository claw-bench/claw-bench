#!/usr/bin/env bash
# Oracle solution for file-013-multi-file-search
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

python3 -c "
import os

docs_dir = '$WORKSPACE/docs'
matches = []

for fname in sorted(os.listdir(docs_dir)):
    if not fname.endswith('.txt'):
        continue
    fpath = os.path.join(docs_dir, fname)
    with open(fpath) as f:
        for i, line in enumerate(f, 1):
            if 'TODO' in line:
                matches.append((fname, i, line.strip()))

matches.sort(key=lambda x: (x[0], x[1]))

lines = []
lines.append('# TODO Search Report')
lines.append('')

file_set = set(m[0] for m in matches)
lines.append(f'Found {len(matches)} matches across {len(file_set)} files.')
lines.append('')
lines.append('| File | Line | Content |')
lines.append('| --- | --- | --- |')
for fname, lineno, content in matches:
    lines.append(f'| {fname} | {lineno} | {content} |')

with open('$WORKSPACE/report.md', 'w') as f:
    f.write('\n'.join(lines) + '\n')
"

echo "Solution written to $WORKSPACE/report.md"
