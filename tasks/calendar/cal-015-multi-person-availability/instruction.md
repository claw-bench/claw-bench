# Task: Multi-Person Availability Coordination

You are given 5 individual calendar files in `workspace/calendars/`:
- `alice.json`
- `bob.json`
- `charlie.json`
- `diana.json`
- `eve.json`

Each calendar contains meetings for the target date **2026-03-25** (and possibly other dates which should be ignored).

Find all **30-minute** common free slots between **09:00** and **17:00** on 2026-03-25 where **all 5 people** are available (no meetings for any person during that slot).

Then recommend the **best** slot based on these criteria (in priority order):
1. Prefer mid-morning (10:00-12:00) or mid-afternoon (14:00-16:00) over early morning or late afternoon
2. If multiple slots tie, pick the earliest one

## Output

Write two files:

**`workspace/common_slots.json`:**
```json
{
  "date": "2026-03-25",
  "duration_minutes": 30,
  "participants": ["alice", "bob", "charlie", "diana", "eve"],
  "slots": [
    {"start_time": "HH:MM", "end_time": "HH:MM"}
  ]
}
```

**`workspace/recommendation.json`:**
```json
{
  "recommended_slot": {"start_time": "HH:MM", "end_time": "HH:MM"},
  "reason": "<brief explanation>"
}
```
