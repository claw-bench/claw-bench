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
      "title": "Sprint Planning",
      "date": "2026-03-16",
      "start_time": "09:00",
      "duration_minutes": 60,
      "participants": ["alice@example.com", "bob@example.com"]
    },
    {
      "id": "mtg-002",
      "title": "Design Review",
      "date": "2026-03-16",
      "start_time": "14:00",
      "duration_minutes": 45,
      "participants": ["charlie@example.com", "alice@example.com"]
    },
    {
      "id": "mtg-003",
      "title": "Cancelled Standup",
      "date": "2026-03-17",
      "start_time": "10:00",
      "duration_minutes": 15,
      "participants": ["alice@example.com", "bob@example.com", "charlie@example.com"]
    },
    {
      "id": "mtg-004",
      "title": "Client Demo",
      "date": "2026-03-18",
      "start_time": "11:00",
      "duration_minutes": 30,
      "participants": ["bob@example.com", "diana@example.com"]
    },
    {
      "id": "mtg-005",
      "title": "Retrospective",
      "date": "2026-03-19",
      "start_time": "15:00",
      "duration_minutes": 60,
      "participants": ["alice@example.com", "bob@example.com", "charlie@example.com"]
    }
  ]
}
JSON

echo "Setup complete for cal-002"
