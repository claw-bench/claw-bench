#!/usr/bin/env bash
# Oracle solution for file-010-directory-tree
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

python3 -c "
import os

def tree(dir_path, prefix=''):
    lines = []
    entries = sorted(os.listdir(dir_path))
    dirs = [e for e in entries if os.path.isdir(os.path.join(dir_path, e))]
    files = [e for e in entries if os.path.isfile(os.path.join(dir_path, e))]

    for d in dirs:
        lines.append(f'{prefix}[DIR] {d}/')
        lines.extend(tree(os.path.join(dir_path, d), prefix + '    '))
    for f in files:
        lines.append(f'{prefix}[FILE] {f}')
    return lines

root = '$WORKSPACE/project'
result = ['project/']
result.extend(tree(root, '    '))

with open('$WORKSPACE/tree.txt', 'w') as f:
    f.write('\n'.join(result) + '\n')
"

echo "Solution written to $WORKSPACE/tree.txt"
