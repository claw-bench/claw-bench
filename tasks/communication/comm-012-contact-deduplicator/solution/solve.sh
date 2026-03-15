#!/usr/bin/env bash
# Oracle solution for comm-012-contact-deduplicator
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
mkdir -p "$WORKSPACE"

python - "$WORKSPACE" << 'PYEOF'
import csv
import re
import sys

ws = sys.argv[1]

def normalize_phone(phone):
    digits = re.sub(r'\D', '', phone)
    if len(digits) == 10:
        return f'({digits[:3]}) {digits[3:6]}-{digits[6:]}'
    return phone

seen_emails = set()
contacts = []

with open(f"{ws}/contacts.csv", 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        email_lower = row['email'].strip().lower()
        if email_lower not in seen_emails:
            seen_emails.add(email_lower)
            contacts.append({
                'name': row['name'].strip().title(),
                'email': email_lower,
                'phone': normalize_phone(row['phone'].strip())
            })

contacts.sort(key=lambda c: c['name'])

with open(f"{ws}/deduplicated_contacts.csv", 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['name', 'email', 'phone'])
    writer.writeheader()
    writer.writerows(contacts)
PYEOF

echo "Solution written to $WORKSPACE/deduplicated_contacts.csv"
