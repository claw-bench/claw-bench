#!/usr/bin/env bash
# Oracle solution for eml-003-count-by-sender
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

cat > "$WORKSPACE/sender_counts.json" <<'JSON'
[
  {"sender": "linda.park@globalcorp.com", "count": 6},
  {"sender": "mike.chen@startupx.io", "count": 4},
  {"sender": "sarah.jones@techwave.com", "count": 3},
  {"sender": "emma.liu@finserve.com", "count": 2},
  {"sender": "noreply@newsletter.dev", "count": 2},
  {"sender": "raj.patel@designhub.co", "count": 2},
  {"sender": "tom.baker@cloudops.net", "count": 1}
]
JSON

echo "Solution written to $WORKSPACE/sender_counts.json"
