#!/usr/bin/env bash
# Oracle solution for eml-016-weekly-digest-generator
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

cat > "$WORKSPACE/digest.json" <<'JSON'
{
  "period": "2026-03-06 to 2026-03-12",
  "total_emails": 8,
  "urgent_count": 2,
  "by_sender": [
    {
      "sender": "alice@company.com",
      "count": 3,
      "subjects": ["Q1 Report Draft", "URGENT: Budget Approval Needed", "Team Lunch Friday"],
      "has_urgent": true
    },
    {
      "sender": "bob@company.com",
      "count": 2,
      "subjects": ["New CI/CD Pipeline Proposal", "Code Review Request: PR #247"],
      "has_urgent": false
    },
    {
      "sender": "carol@company.com",
      "count": 2,
      "subjects": ["Updated Design Mockups", "Urgent: Production Server Outage"],
      "has_urgent": true
    },
    {
      "sender": "dave@company.com",
      "count": 1,
      "subjects": ["Onboarding Documentation Updates"],
      "has_urgent": false
    }
  ]
}
JSON

echo "Solution written to $WORKSPACE/digest.json"
