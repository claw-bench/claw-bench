#!/usr/bin/env bash
# Oracle solution for eml-018-expense-receipt-emails
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

cat > "$WORKSPACE/expense_report.json" <<'JSON'
{
  "expenses": [
    {
      "vendor": "Amazon",
      "amount": 45.99,
      "date": "2026-03-08",
      "category": "office-supplies"
    },
    {
      "vendor": "Starbucks",
      "amount": 12.50,
      "date": "2026-03-09",
      "category": "meals"
    },
    {
      "vendor": "Uber",
      "amount": 23.75,
      "date": "2026-03-10",
      "category": "transportation"
    },
    {
      "vendor": "AWS",
      "amount": 156.00,
      "date": "2026-03-07",
      "category": "cloud-services"
    },
    {
      "vendor": "Office Depot",
      "amount": 89.30,
      "date": "2026-03-11",
      "category": "office-supplies"
    },
    {
      "vendor": "Zoom",
      "amount": 14.99,
      "date": "2026-03-06",
      "category": "software"
    }
  ],
  "total": 342.53,
  "by_category": {
    "office-supplies": 135.29,
    "meals": 12.50,
    "transportation": 23.75,
    "cloud-services": 156.00,
    "software": 14.99
  }
}
JSON

echo "Solution written to $WORKSPACE/expense_report.json"
