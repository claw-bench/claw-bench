#!/usr/bin/env bash
# Oracle solution for eml-007-filter-sort-inbox
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

cat > "$WORKSPACE/filtered_inbox.json" <<'JSON'
[
  {"id": 19, "from": "ceo@company.com", "subject": "All-hands meeting", "date": "2026-03-06T10:00:00Z", "important": true, "body": "Company all-hands this Friday."},
  {"id": 17, "from": "alerts@monitoring.com", "subject": "Server load warning", "date": "2026-03-06T22:00:00Z", "important": true, "body": "Server CPU at 95%."},
  {"id": 16, "from": "partner@startup.io", "subject": "Partnership proposal", "date": "2026-03-07T09:00:00Z", "important": true, "body": "We'd like to discuss a partnership."},
  {"id": 15, "from": "legal@company.com", "subject": "NDA review required", "date": "2026-03-07T11:00:00Z", "important": true, "body": "Please review and sign the NDA."},
  {"id": 13, "from": "team@company.com", "subject": "Sprint planning", "date": "2026-03-08T08:00:00Z", "important": true, "body": "Sprint planning meeting at 2 PM."},
  {"id": 12, "from": "cto@company.com", "subject": "System outage postmortem", "date": "2026-03-08T10:00:00Z", "important": true, "body": "Please review the postmortem document."},
  {"id": 10, "from": "finance@company.com", "subject": "Expense report overdue", "date": "2026-03-09T09:00:00Z", "important": true, "body": "Please submit your expense report."},
  {"id": 8, "from": "manager@company.com", "subject": "Performance review scheduled", "date": "2026-03-09T15:00:00Z", "important": true, "body": "Your review is next week."},
  {"id": 7, "from": "security@company.com", "subject": "Password expiry notice", "date": "2026-03-10T08:00:00Z", "important": true, "body": "Your password expires in 3 days."},
  {"id": 5, "from": "client@bigco.com", "subject": "Contract renewal urgent", "date": "2026-03-10T16:00:00Z", "important": true, "body": "We need to discuss the contract terms."},
  {"id": 3, "from": "hr@company.com", "subject": "Benefits enrollment deadline", "date": "2026-03-11T14:00:00Z", "important": true, "body": "Reminder: benefits enrollment closes Friday."},
  {"id": 1, "from": "ceo@company.com", "subject": "Board meeting prep", "date": "2026-03-12T09:00:00Z", "important": true, "body": "Please prepare the board presentation."}
]
JSON

echo "Solution written to $WORKSPACE/filtered_inbox.json"
