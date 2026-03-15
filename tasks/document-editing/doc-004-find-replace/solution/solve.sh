#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${1:-workspace}"

python3 -c "
import json, re

with open('$WORKSPACE/document.txt') as f:
    text = f.read()
with open('$WORKSPACE/replacements.json') as f:
    rules = json.load(f)

for rule in rules:
    text = re.sub(rule['pattern'], rule['replacement'], text)

with open('$WORKSPACE/result.txt', 'w') as f:
    f.write(text)
"

echo "Solution written to $WORKSPACE/result.txt"
