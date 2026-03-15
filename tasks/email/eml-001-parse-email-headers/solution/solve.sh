#!/usr/bin/env bash
# Oracle solution for eml-001-parse-email-headers
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

cat > "$WORKSPACE/headers.json" <<'JSON'
{
  "from": "alice.johnson@techcorp.com",
  "to": "bob.smith@techcorp.com",
  "subject": "Q1 Budget Review Meeting",
  "date": "Tue, 10 Mar 2026 14:30:00 +0000",
  "cc": ["carol.white@techcorp.com", "dave.brown@techcorp.com"]
}
JSON

echo "Solution written to $WORKSPACE/headers.json"
