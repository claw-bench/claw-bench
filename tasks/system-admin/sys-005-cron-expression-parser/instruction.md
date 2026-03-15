# Task: Cron Expression Parser

You are given a file at `workspace/crontab.txt` containing 8 crontab entries. Parse each entry and generate a human-readable explanation.

## Requirements

1. Read `workspace/crontab.txt`.
2. Parse each non-comment, non-empty line as a cron entry in the format:
   ```
   minute hour day_of_month month day_of_week command
   ```
3. Generate a JSON report with the following structure:

```json
{
  "entries": [
    {
      "expression": "<the 5-field cron expression>",
      "command": "<the command>",
      "description": "<human-readable schedule description>",
      "next_runs": ["<ISO 8601 datetime>", "<ISO 8601 datetime>", "<ISO 8601 datetime>"]
    },
    ...
  ],
  "total_entries": <count>
}
```

4. Each `description` must be a clear English explanation of when the job runs.
   - Example: `0 2 * * *` -> "Every day at 2:00 AM"
   - Example: `*/15 * * * *` -> "Every 15 minutes"
   - Example: `0 0 1 * *` -> "At midnight on the 1st of every month"
5. `next_runs` should contain 3 upcoming run times starting from `2024-03-15T12:00:00`, in ISO 8601 format (YYYY-MM-DDTHH:MM:SS).

## Cron Field Reference

- Minute: 0-59
- Hour: 0-23
- Day of month: 1-31
- Month: 1-12
- Day of week: 0-7 (0 and 7 = Sunday)
- Special characters: `*` (any), `*/n` (every n), `,` (list), `-` (range)

## Output

Save the report to `workspace/cron_explained.json`.
