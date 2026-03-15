#!/usr/bin/env bash
# Oracle solution for file-006-extract-emails
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

python3 -c "
import re

with open('$WORKSPACE/document.txt') as f:
    text = f.read()

emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
emails = sorted(set(emails))

with open('$WORKSPACE/emails.txt', 'w') as f:
    f.write('\n'.join(emails) + '\n')
"

echo "Solution written to $WORKSPACE/emails.txt"
