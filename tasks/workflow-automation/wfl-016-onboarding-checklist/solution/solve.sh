#!/usr/bin/env bash
# Oracle solution for wfl-016-onboarding-checklist
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

python3 -c "
import json
from datetime import datetime, timedelta

with open('$WORKSPACE/new_hire.json') as f:
    hire = json.load(f)

with open('$WORKSPACE/templates/equipment_by_dept.json') as f:
    equip = json.load(f)

# Account setup
username = hire['email'].split('@')[0]
dept_lower = hire['department'].lower()
account = {
    'username': username,
    'email': hire['email'],
    'groups': [dept_lower, 'all-staff'],
    'access_level': 'developer' if hire['department'] == 'Engineering' else 'standard'
}
with open('$WORKSPACE/account_setup.json', 'w') as f:
    json.dump(account, f, indent=2)

# Welcome email
first_name = hire['name'].split()[0]
body = (
    f\"Dear {hire['name']},\n\n\"
    f\"Welcome to the {hire['department']} team! We are excited to have you join us \"
    f\"on {hire['start_date']}. Your manager, {hire['manager']}, will help you get \"
    f\"settled in during your first week.\n\n\"
    f\"Best regards,\nHR Team\"
)
email = {
    'to': hire['email'],
    'cc': hire['manager_email'],
    'subject': f'Welcome to the team, {first_name}!',
    'body': body
}
with open('$WORKSPACE/welcome_email.json', 'w') as f:
    json.dump(email, f, indent=2)

# Equipment request
start = datetime.strptime(hire['start_date'], '%Y-%m-%d')
delivery = start - timedelta(days=3)
equip_req = {
    'employee': hire['name'],
    'department': hire['department'],
    'items': equip[hire['department']],
    'delivery_date': delivery.strftime('%Y-%m-%d')
}
with open('$WORKSPACE/equipment_request.json', 'w') as f:
    json.dump(equip_req, f, indent=2)
"

echo "Solution written to $WORKSPACE/"
