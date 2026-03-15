#!/usr/bin/env bash
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
mkdir -p "$WORKSPACE"

cat > "$WORKSPACE/draft_schedule.json" <<'JSON'
{
  "meetings": [
    {"id": "draft-01", "title": "Monday Standup", "duration_minutes": 15, "topic": "standup", "fixed": true, "date": "2026-03-16", "start_time": "09:00", "end_time": "09:15"},
    {"id": "draft-02", "title": "Tuesday Standup", "duration_minutes": 15, "topic": "standup", "fixed": true, "date": "2026-03-17", "start_time": "09:00", "end_time": "09:15"},
    {"id": "draft-03", "title": "Wednesday Standup", "duration_minutes": 15, "topic": "standup", "fixed": true, "date": "2026-03-18", "start_time": "09:00", "end_time": "09:15"},
    {"id": "draft-04", "title": "Thursday Standup", "duration_minutes": 15, "topic": "standup", "fixed": true, "date": "2026-03-19", "start_time": "09:00", "end_time": "09:15"},
    {"id": "draft-05", "title": "Friday Standup", "duration_minutes": 15, "topic": "standup", "fixed": true, "date": "2026-03-20", "start_time": "09:00", "end_time": "09:15"},
    {"id": "draft-06", "title": "Sprint Planning", "duration_minutes": 90, "topic": "sprint", "fixed": true, "date": "2026-03-16", "start_time": "10:00", "end_time": "11:30"},
    {"id": "draft-07", "title": "Sprint Review", "duration_minutes": 60, "topic": "sprint", "preferred_day": "2026-03-20"},
    {"id": "draft-08", "title": "Sprint Retro", "duration_minutes": 45, "topic": "sprint", "preferred_day": "2026-03-20"},
    {"id": "draft-09", "title": "Architecture Review", "duration_minutes": 90, "topic": "engineering"},
    {"id": "draft-10", "title": "Code Review Session", "duration_minutes": 60, "topic": "engineering"},
    {"id": "draft-11", "title": "Tech Debt Discussion", "duration_minutes": 45, "topic": "engineering"},
    {"id": "draft-12", "title": "Client Demo", "duration_minutes": 60, "topic": "client", "preferred_day": "2026-03-19"},
    {"id": "draft-13", "title": "Client Feedback Review", "duration_minutes": 30, "topic": "client", "preferred_day": "2026-03-19"},
    {"id": "draft-14", "title": "Product Roadmap", "duration_minutes": 60, "topic": "product"},
    {"id": "draft-15", "title": "Feature Prioritization", "duration_minutes": 45, "topic": "product"},
    {"id": "draft-16", "title": "Design Review", "duration_minutes": 60, "topic": "design"},
    {"id": "draft-17", "title": "UX Research Findings", "duration_minutes": 30, "topic": "design"},
    {"id": "draft-18", "title": "1:1 with Manager", "duration_minutes": 30, "topic": "personal", "preferred_day": "2026-03-18"},
    {"id": "draft-19", "title": "Team Building", "duration_minutes": 60, "topic": "social", "preferred_day": "2026-03-20"},
    {"id": "draft-20", "title": "Budget Review", "duration_minutes": 45, "topic": "admin"}
  ]
}
JSON

cat > "$WORKSPACE/preferences.json" <<'JSON'
{
  "business_hours": {"start": "09:00", "end": "17:00"},
  "min_gap_after_long_meetings_minutes": 15,
  "long_meeting_threshold_minutes": 60,
  "preferred_focus_blocks": [
    {"day": "2026-03-17", "start": "13:00", "end": "15:00", "description": "Deep work block - avoid meetings"}
  ]
}
JSON

echo "Setup complete for cal-014"
