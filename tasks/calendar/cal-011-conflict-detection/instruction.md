# Task: Conflict Detection

You are given a calendar file at `workspace/calendar.json` containing 12 meetings. Some of these meetings have overlapping time slots.

Detect all scheduling conflicts (pairs of meetings whose time ranges overlap on the same date) and write them to `workspace/conflicts.json`.

Each conflict should be represented as:
```json
{
  "meeting_a": "<id>",
  "meeting_b": "<id>",
  "date": "YYYY-MM-DD",
  "overlap_start": "HH:MM",
  "overlap_end": "HH:MM",
  "overlap_minutes": <integer>
}
```

For each conflicting pair, `meeting_a` should be the meeting with the earlier `start_time` (or the lexicographically smaller id if they start at the same time). Do not list the same pair twice.

## Output

Write to `workspace/conflicts.json` as a JSON object with a `"conflicts"` key containing the array of conflict objects, sorted by date then by `meeting_a` id.
