#!/usr/bin/env bash
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
mkdir -p "$WORKSPACE"

cat > "$WORKSPACE/calendar.json" <<'JSON'
{
  "meetings": [
    {
      "id": "mtg-001",
      "title": "Team Standup",
      "date": "2026-03-20",
      "start_time": "09:00",
      "duration_minutes": 15,
      "participants": ["alice@example.com"],
      "tags": ["team", "daily"]
    },
    {
      "id": "mtg-002",
      "title": "Client Presentation",
      "date": "2026-03-20",
      "start_time": "11:00",
      "duration_minutes": 60,
      "participants": ["alice@example.com", "diana@example.com"],
      "tags": ["client", "external"]
    },
    {
      "id": "mtg-003",
      "title": "Sprint Review",
      "date": "2026-03-21",
      "start_time": "14:00",
      "duration_minutes": 45,
      "participants": ["bob@example.com", "charlie@example.com"],
      "tags": ["team", "sprint"]
    },
    {
      "id": "mtg-004",
      "title": "1:1 Manager",
      "date": "2026-03-21",
      "start_time": "16:00",
      "duration_minutes": 30,
      "participants": ["alice@example.com"],
      "tags": ["personal"]
    },
    {
      "id": "mtg-005",
      "title": "Team Retrospective",
      "date": "2026-03-22",
      "start_time": "10:00",
      "duration_minutes": 60,
      "participants": ["alice@example.com", "bob@example.com"],
      "tags": ["team", "sprint"]
    }
  ]
}
JSON

cat > "$WORKSPACE/contacts.json" <<'JSON'
{
  "contacts": [
    {"name": "Alice Smith", "email": "alice@example.com"},
    {"name": "Bob Jones", "email": "bob@example.com"},
    {"name": "Charlie Brown", "email": "charlie@example.com"},
    {"name": "Diana Prince", "email": "diana@example.com"}
  ]
}
JSON

echo "Setup complete for cal-008"
