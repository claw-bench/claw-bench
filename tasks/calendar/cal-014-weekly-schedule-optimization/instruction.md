# Task: Weekly Schedule Optimization

You are given:
- `workspace/draft_schedule.json` — 20 proposed meetings for the week of 2026-03-16 to 2026-03-20
- `workspace/preferences.json` — scheduling preferences and constraints

Optimize the schedule by assigning each meeting to a specific date and time slot, following these rules:

## Rules

1. **No conflicts:** No two meetings may overlap in the optimized schedule.
2. **Business hours only:** All meetings must be scheduled between 09:00 and 17:00.
3. **All meetings included:** Every meeting from the draft must appear in the optimized schedule.
4. **Respect fixed meetings:** Meetings with `"fixed": true` must keep their original date and time.
5. **Respect day preferences:** If a meeting has a `"preferred_day"` field, schedule it on that day if possible.
6. **Topic grouping:** Meetings with the same `"topic"` should be scheduled on the same day when possible.
7. **No back-to-back for long meetings:** Meetings longer than 60 minutes should have at least a 15-minute gap after them.

## Output

Write the optimized schedule to `workspace/optimized_schedule.json` as a JSON object with a `"meetings"` array. Each meeting must retain all its original fields and have updated `"date"` and `"start_time"` / `"end_time"` fields.
