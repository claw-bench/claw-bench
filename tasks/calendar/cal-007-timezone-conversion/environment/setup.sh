#!/usr/bin/env bash
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
mkdir -p "$WORKSPACE"

cat > "$WORKSPACE/calendar.json" <<'JSON'
{
  "timezone": "UTC",
  "meetings": [
    {
      "id": "mtg-001",
      "title": "Morning Sync",
      "date": "2026-03-20",
      "start_time": "15:00",
      "end_time": "15:30",
      "duration_minutes": 30,
      "participants": ["alice@example.com"]
    },
    {
      "id": "mtg-002",
      "title": "Design Review",
      "date": "2026-03-20",
      "start_time": "20:00",
      "end_time": "21:00",
      "duration_minutes": 60,
      "participants": ["bob@example.com"]
    },
    {
      "id": "mtg-003",
      "title": "Client Call",
      "date": "2026-03-21",
      "start_time": "00:00",
      "end_time": "01:00",
      "duration_minutes": 60,
      "participants": ["charlie@example.com"]
    },
    {
      "id": "mtg-004",
      "title": "Sprint Planning",
      "date": "2026-03-21",
      "start_time": "17:00",
      "end_time": "18:00",
      "duration_minutes": 60,
      "participants": ["alice@example.com", "bob@example.com"]
    },
    {
      "id": "mtg-005",
      "title": "Lunch Meeting",
      "date": "2026-03-22",
      "start_time": "19:00",
      "end_time": "19:30",
      "duration_minutes": 30,
      "participants": ["diana@example.com"]
    },
    {
      "id": "mtg-006",
      "title": "Early Standup",
      "date": "2026-03-20",
      "start_time": "05:00",
      "end_time": "05:15",
      "duration_minutes": 15,
      "participants": ["eve@example.com"]
    }
  ]
}
JSON

echo "Setup complete for cal-007"
