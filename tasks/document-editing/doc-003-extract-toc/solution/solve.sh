#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${1:-workspace}"

python3 -c "
import json, re

with open('$WORKSPACE/document.md') as f:
    lines = f.readlines()

toc = []
for line in lines:
    m = re.match(r'^(#{1,6})\s+(.+)', line.strip())
    if m:
        level = len(m.group(1))
        title = m.group(2).strip()
        slug = re.sub(r'[^a-z0-9\s-]', '', title.lower())
        slug = re.sub(r'\s+', '-', slug).strip('-')
        toc.append({'level': level, 'title': title, 'slug': slug})

with open('$WORKSPACE/toc.json', 'w') as f:
    json.dump(toc, f, indent=2)
"

echo "Solution written to $WORKSPACE/toc.json"
