#!/usr/bin/env bash
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
mkdir -p "$WORKSPACE"

cat > "$WORKSPACE/calendar.json" <<'JSON'
{
  "meetings": [
    {"id": "mtg-01", "title": "Standup", "date": "2026-03-20", "start_time": "09:00", "end_time": "09:15", "duration_minutes": 15},
    {"id": "mtg-02", "title": "Sprint Planning", "date": "2026-03-20", "start_time": "09:00", "end_time": "10:30", "duration_minutes": 90},
    {"id": "mtg-03", "title": "Design Review", "date": "2026-03-20", "start_time": "10:00", "end_time": "11:00", "duration_minutes": 60},
    {"id": "mtg-04", "title": "Lunch", "date": "2026-03-20", "start_time": "12:00", "end_time": "13:00", "duration_minutes": 60},
    {"id": "mtg-05", "title": "Client Call", "date": "2026-03-20", "start_time": "14:00", "end_time": "15:00", "duration_minutes": 60},
    {"id": "mtg-06", "title": "Code Review", "date": "2026-03-20", "start_time": "14:30", "end_time": "15:30", "duration_minutes": 60},
    {"id": "mtg-07", "title": "Team Sync", "date": "2026-03-20", "start_time": "16:00", "end_time": "16:30", "duration_minutes": 30},
    {"id": "mtg-08", "title": "Morning Brief", "date": "2026-03-21", "start_time": "08:30", "end_time": "09:00", "duration_minutes": 30},
    {"id": "mtg-09", "title": "Workshop", "date": "2026-03-21", "start_time": "09:00", "end_time": "11:00", "duration_minutes": 120},
    {"id": "mtg-10", "title": "Budget Review", "date": "2026-03-21", "start_time": "10:00", "end_time": "11:30", "duration_minutes": 90},
    {"id": "mtg-11", "title": "Training", "date": "2026-03-21", "start_time": "10:30", "end_time": "12:00", "duration_minutes": 90},
    {"id": "mtg-12", "title": "Wrap-up", "date": "2026-03-21", "start_time": "15:00", "end_time": "15:30", "duration_minutes": 30}
  ]
}
JSON

echo "Setup complete for cal-011"
