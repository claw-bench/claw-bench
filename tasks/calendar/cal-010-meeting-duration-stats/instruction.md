# Task: Meeting Duration Statistics

You are given a calendar file at `workspace/calendar.json` containing 15 meetings spread over 5 days.

Compute the following statistics and write them to `workspace/calendar_stats.json`:

- `total_meetings`: total number of meetings
- `total_hours`: total meeting hours (sum of all durations, as a float)
- `average_duration_minutes`: average meeting duration in minutes (as a float, rounded to 1 decimal place)
- `busiest_day`: the date with the most total meeting hours (if tie, pick the earliest date)
- `busiest_day_hours`: total meeting hours on the busiest day (as a float)
- `shortest_meeting_minutes`: duration of the shortest meeting
- `longest_meeting_minutes`: duration of the longest meeting

## Output

Write the statistics to `workspace/calendar_stats.json` as a flat JSON object.
