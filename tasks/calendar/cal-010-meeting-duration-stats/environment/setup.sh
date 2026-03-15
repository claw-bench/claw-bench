#!/usr/bin/env bash
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
mkdir -p "$WORKSPACE"

cat > "$WORKSPACE/calendar.json" <<'JSON'
{
  "meetings": [
    {"id": "mtg-01", "title": "Standup", "date": "2026-03-16", "start_time": "09:00", "duration_minutes": 15},
    {"id": "mtg-02", "title": "Sprint Planning", "date": "2026-03-16", "start_time": "10:00", "duration_minutes": 120},
    {"id": "mtg-03", "title": "Design Review", "date": "2026-03-16", "start_time": "14:00", "duration_minutes": 60},
    {"id": "mtg-04", "title": "Standup", "date": "2026-03-17", "start_time": "09:00", "duration_minutes": 15},
    {"id": "mtg-05", "title": "Client Call", "date": "2026-03-17", "start_time": "11:00", "duration_minutes": 45},
    {"id": "mtg-06", "title": "Architecture Review", "date": "2026-03-17", "start_time": "14:00", "duration_minutes": 90},
    {"id": "mtg-07", "title": "Standup", "date": "2026-03-18", "start_time": "09:00", "duration_minutes": 15},
    {"id": "mtg-08", "title": "Workshop", "date": "2026-03-18", "start_time": "10:00", "duration_minutes": 180},
    {"id": "mtg-09", "title": "1:1 Manager", "date": "2026-03-18", "start_time": "15:00", "duration_minutes": 30},
    {"id": "mtg-10", "title": "Standup", "date": "2026-03-19", "start_time": "09:00", "duration_minutes": 15},
    {"id": "mtg-11", "title": "Code Review", "date": "2026-03-19", "start_time": "10:30", "duration_minutes": 45},
    {"id": "mtg-12", "title": "Team Lunch", "date": "2026-03-19", "start_time": "12:00", "duration_minutes": 60},
    {"id": "mtg-13", "title": "Standup", "date": "2026-03-20", "start_time": "09:00", "duration_minutes": 15},
    {"id": "mtg-14", "title": "Retrospective", "date": "2026-03-20", "start_time": "14:00", "duration_minutes": 60},
    {"id": "mtg-15", "title": "Demo", "date": "2026-03-20", "start_time": "16:00", "duration_minutes": 45}
  ]
}
JSON

echo "Setup complete for cal-010"
