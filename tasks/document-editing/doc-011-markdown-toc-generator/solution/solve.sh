#!/usr/bin/env bash
# Oracle solution for doc-011-markdown-toc-generator
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
mkdir -p "$WORKSPACE"

python - "$WORKSPACE" << 'PYEOF'
import re
import sys

ws = sys.argv[1]

with open(f'{ws}/document.md', 'r') as f:
    content = f.read()

lines = content.splitlines()
toc_entries = []

for line in lines:
    m = re.match(r'^(#{2,4})\s+(.+)$', line)
    if m:
        level = len(m.group(1))
        text = m.group(2).strip()
        anchor = re.sub(r'[^a-z0-9\s-]', '', text.lower())
        anchor = re.sub(r'\s+', '-', anchor.strip())
        indent = '  ' * (level - 2)
        toc_entries.append(f'{indent}- [{text}](#{anchor})')

toc = '## Table of Contents\n' + '\n'.join(toc_entries) + '\n'

with open(f'{ws}/document_with_toc.md', 'w') as f:
    f.write(toc + '\n' + content)
PYEOF

echo "Solution written to $WORKSPACE/document_with_toc.md"
