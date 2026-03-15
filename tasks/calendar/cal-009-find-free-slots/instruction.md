# Task: Find Free Slots

You are given a calendar file at `workspace/calendar.json` containing meetings on **2026-03-20**.

Find all available **30-minute** time slots between **09:00** and **17:00** (business hours) on that day that do not overlap with any existing meeting.

Each free slot should be represented as:
```json
{
  "start_time": "HH:MM",
  "end_time": "HH:MM",
  "duration_minutes": 30
}
```

## Output

Write the free slots to `workspace/free_slots.json` as a JSON object with a `"date"` field set to `"2026-03-20"` and a `"slots"` key containing the array of free slots, sorted by `start_time`.
