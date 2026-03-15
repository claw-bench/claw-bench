#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${1:-workspace}"

python3 -c "
import json

with open('$WORKSPACE/contacts_a.json') as f:
    a = json.load(f)
with open('$WORKSPACE/contacts_b.json') as f:
    b = json.load(f)

merged = {}
for c in a:
    merged[c['email'].lower()] = c
for c in b:
    merged[c['email'].lower()] = c

result = sorted(merged.values(), key=lambda x: x['email'].lower())
with open('$WORKSPACE/merged_contacts.json', 'w') as f:
    json.dump(result, f, indent=2)
"

echo "Solution written to $WORKSPACE/merged_contacts.json"
