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
      "title": "Morning Standup",
      "date": "2026-03-20",
      "start_time": "09:00",
      "end_time": "09:30",
      "duration_minutes": 30
    },
    {
      "id": "mtg-002",
      "title": "Project Review",
      "date": "2026-03-20",
      "start_time": "10:00",
      "end_time": "11:30",
      "duration_minutes": 90
    },
    {
      "id": "mtg-003",
      "title": "Lunch Meeting",
      "date": "2026-03-20",
      "start_time": "12:00",
      "end_time": "13:00",
      "duration_minutes": 60
    },
    {
      "id": "mtg-004",
      "title": "Architecture Discussion",
      "date": "2026-03-20",
      "start_time": "14:00",
      "end_time": "15:30",
      "duration_minutes": 90
    }
  ]
}
JSON

echo "Setup complete for cal-009"
