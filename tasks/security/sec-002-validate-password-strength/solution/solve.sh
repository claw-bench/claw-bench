#!/usr/bin/env bash
# Oracle solution for sec-002-validate-password-strength
set -euo pipefail

WORKSPACE="${1:-workspace}"

python3 -c "
import json
import re
import string

def check_password(pw):
    reasons = []
    if len(pw) < 12:
        reasons.append('too short')
    if not re.search(r'[A-Z]', pw):
        reasons.append('missing uppercase')
    if not re.search(r'[a-z]', pw):
        reasons.append('missing lowercase')
    if not re.search(r'[0-9]', pw):
        reasons.append('missing digit')
    special = set(string.punctuation)
    if not any(c in special for c in pw):
        reasons.append('missing special character')
    return 'pass' if not reasons else 'fail', reasons

with open('$WORKSPACE/passwords.txt') as f:
    passwords = [line.strip() for line in f if line.strip()]

results = []
for pw in passwords:
    status, reasons = check_password(pw)
    results.append({'password': pw, 'status': status, 'reasons': reasons})

with open('$WORKSPACE/results.json', 'w') as f:
    json.dump(results, f, indent=2)
"

echo "Solution written to $WORKSPACE/results.json"
