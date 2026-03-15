#!/usr/bin/env bash
# Oracle solution for eml-013-signature-extractor
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

python - "$WORKSPACE" << 'PYEOF'
import sys
import json
import re

ws = sys.argv[1]

with open(f'{ws}/emails.txt') as f:
    content = f.read()

# Split emails by --- separator (on its own line)
raw_emails = re.split(r'\n---\n', content.strip())

signatures = {}

for email_text in raw_emails:
    email_text = email_text.strip()
    if not email_text:
        continue

    # Extract From header
    from_match = re.search(r'^From:\s*(.+)$', email_text, re.MULTILINE)
    if not from_match:
        continue
    sender = from_match.group(1).strip()

    # Find signature delimiter (-- on its own line)
    # Split body from headers first
    parts = email_text.split('\n\n', 1)
    if len(parts) < 2:
        signatures[sender] = ''
        continue

    body = parts[1]

    # Look for -- on its own line as signature delimiter
    sig_parts = re.split(r'^--$', body, maxsplit=1, flags=re.MULTILINE)
    if len(sig_parts) >= 2:
        signatures[sender] = sig_parts[1].strip()
    else:
        signatures[sender] = ''

with open(f'{ws}/signatures.json', 'w') as f:
    json.dump(signatures, f, indent=2)
PYEOF

echo "Signatures extracted to $WORKSPACE/signatures.json"
