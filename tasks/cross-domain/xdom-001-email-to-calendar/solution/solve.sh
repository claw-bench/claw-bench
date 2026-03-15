#!/usr/bin/env bash
# Oracle solution for xdom-001-email-to-calendar
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

cat > "$WORKSPACE/calendar_entries.json" <<'JSON'
[
  {
    "subject": "Q1 Planning Meeting",
    "date": "2026-04-01",
    "start_time": "10:00",
    "duration_minutes": 90,
    "participants": ["bob@techcorp.com", "carol@techcorp.com"],
    "organizer": "alice@techcorp.com"
  },
  {
    "subject": "Sprint Retrospective",
    "date": "2026-04-03",
    "start_time": "14:00",
    "duration_minutes": 60,
    "participants": ["alice@techcorp.com", "carol@techcorp.com", "dave@techcorp.com"],
    "organizer": "bob@techcorp.com"
  },
  {
    "subject": "Design Review Session",
    "date": "2026-04-07",
    "start_time": "11:30",
    "duration_minutes": 45,
    "participants": ["bob@techcorp.com", "eve@techcorp.com"],
    "organizer": "dave@techcorp.com"
  },
  {
    "subject": "Client Demo Preparation",
    "date": "2026-04-10",
    "start_time": "15:00",
    "duration_minutes": 120,
    "participants": ["alice@techcorp.com", "bob@techcorp.com", "dave@techcorp.com", "eve@techcorp.com"],
    "organizer": "carol@techcorp.com"
  }
]
JSON

echo "Solution written to $WORKSPACE/calendar_entries.json"
