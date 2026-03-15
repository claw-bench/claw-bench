#!/usr/bin/env bash
# Oracle solution for cal-001-create-meeting
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

cat > "$WORKSPACE/meeting.json" <<'JSON'
{
  "title": "Weekly Sync",
  "date": "2026-03-20",
  "start_time": "10:00",
  "duration_minutes": 30,
  "participants": [
    "alice@example.com",
    "bob@example.com"
  ]
}
JSON

echo "Solution written to $WORKSPACE/meeting.json"
