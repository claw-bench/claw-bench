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
      "title": "Project Kickoff",
      "date": "2026-03-16",
      "start_time": "09:30",
      "duration_minutes": 60,
      "participants": ["alice@example.com", "bob@example.com", "charlie@example.com"],
      "location": "Conference Room A"
    },
    {
      "id": "mtg-002",
      "title": "Budget Review",
      "date": "2026-03-17",
      "start_time": "11:00",
      "duration_minutes": 45,
      "participants": ["diana@example.com", "eve@example.com"],
      "location": "Room B"
    },
    {
      "id": "mtg-003",
      "title": "Architecture Discussion",
      "date": "2026-03-18",
      "start_time": "14:00",
      "duration_minutes": 90,
      "participants": ["alice@example.com", "frank@example.com"],
      "location": "Room C"
    }
  ]
}
JSON

echo "Setup complete for cal-005"
