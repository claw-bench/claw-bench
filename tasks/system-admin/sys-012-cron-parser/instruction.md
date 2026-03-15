# Task: Cron Parser

You are given a file at `workspace/crontab.txt` containing crontab entries, some with comments.

## Requirements

1. Read `workspace/crontab.txt`.
2. Parse each non-comment, non-empty line as a cron entry.
3. Lines starting with `#` are comments and should be ignored.
4. Generate a JSON report saved to `workspace/cron_schedule.json` with the following structure:

```json
{
  "jobs": [
    {
      "command": "<the command portion>",
      "schedule_human": "<human-readable description>",
      "cron_expression": "<normalized 5-field cron expression>"
    },
    ...
  ],
  "total_jobs": <number of jobs>
}
```

5. The `schedule_human` field should describe when the job runs in plain English. Examples:
   - `0 * * * *` -> "Every hour at minute 0"
   - `30 2 * * *` -> "Daily at 02:30"
   - `0 0 * * 0` -> "Weekly on Sunday at 00:00"
   - `*/15 * * * *` -> "Every 15 minutes"
   - `0 0 1 * *` -> "Monthly on day 1 at 00:00"
   - `0 3 * * 1-5` -> "Weekdays at 03:00"
   - `0 0 1 1 *` -> "Yearly on January 1 at 00:00"
   - `0 6,18 * * *` -> "Daily at 06:00 and 18:00"

6. The `cron_expression` field should contain the first 5 space-separated fields of the cron line (minute, hour, day-of-month, month, day-of-week).

## Output

Save the report to `workspace/cron_schedule.json`.
