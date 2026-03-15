#!/usr/bin/env bash
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
mkdir -p "$WORKSPACE"

cat > "$WORKSPACE/calendar.json" <<'JSON'
{
  "events": [
    {"id": "evt-01", "title": "Morning Standup", "date": "2026-03-15", "start_time": "09:00", "duration_minutes": 15, "location": "Room A"},
    {"id": "evt-02", "title": "Sprint Review", "date": "2026-03-14", "start_time": "14:00", "duration_minutes": 60, "location": "Room B"},
    {"id": "evt-03", "title": "Lunch with Client", "date": "2026-03-15", "start_time": "12:00", "duration_minutes": 60, "location": "Restaurant"},
    {"id": "evt-04", "title": "Team Building", "date": "2026-03-16", "start_time": "10:00", "duration_minutes": 120, "location": "Park"},
    {"id": "evt-05", "title": "Code Review", "date": "2026-03-15", "start_time": "15:30", "duration_minutes": 45, "location": "Room C"},
    {"id": "evt-06", "title": "Budget Meeting", "date": "2026-03-17", "start_time": "11:00", "duration_minutes": 30, "location": "Room A"},
    {"id": "evt-07", "title": "1:1 with Manager", "date": "2026-03-15", "start_time": "10:30", "duration_minutes": 30, "location": "Office"},
    {"id": "evt-08", "title": "Design Workshop", "date": "2026-03-14", "start_time": "09:00", "duration_minutes": 90, "location": "Room D"},
    {"id": "evt-09", "title": "End of Day Wrap-up", "date": "2026-03-15", "start_time": "17:00", "duration_minutes": 15, "location": "Room A"},
    {"id": "evt-10", "title": "Planning Poker", "date": "2026-03-16", "start_time": "13:00", "duration_minutes": 60, "location": "Room B"}
  ]
}
JSON

echo "Setup complete for cal-003"
