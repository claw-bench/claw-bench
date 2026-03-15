#!/usr/bin/env bash
# Oracle solution for eml-004-classify-emails
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

cat > "$WORKSPACE/classified.json" <<'JSON'
[
  {"email_id": 1, "category": "work"},
  {"email_id": 2, "category": "personal"},
  {"email_id": 3, "category": "newsletter"},
  {"email_id": 4, "category": "spam"},
  {"email_id": 5, "category": "work"},
  {"email_id": 6, "category": "personal"},
  {"email_id": 7, "category": "newsletter"},
  {"email_id": 8, "category": "spam"},
  {"email_id": 9, "category": "work"},
  {"email_id": 10, "category": "personal"},
  {"email_id": 11, "category": "spam"},
  {"email_id": 12, "category": "newsletter"},
  {"email_id": 13, "category": "work"},
  {"email_id": 14, "category": "personal"},
  {"email_id": 15, "category": "work"}
]
JSON

echo "Solution written to $WORKSPACE/classified.json"
