# Task: Log Rotation Planner

You are given a file at `workspace/log_inventory.json` containing an array of log file records.

## Requirements

1. Read `workspace/log_inventory.json`.
2. Each record has: `path`, `size_mb`, `last_modified` (ISO date string YYYY-MM-DD), and `retention_days`.
3. Using a reference date of **2025-03-01**, determine the age of each file in days.
4. Apply these rules to each file:
   - **rotate**: if `size_mb >= 100` (size threshold) OR age in days > `retention_days`
   - **compress**: if the file should be rotated AND `size_mb >= 50`
   - **delete**: if age in days > `retention_days * 2` (double the retention period)
5. A file can have multiple actions. For example, a large old file might be marked for all three.
6. Generate `workspace/rotation_plan.json` with this structure:

```json
{
  "reference_date": "2025-03-01",
  "files": [
    {
      "path": "<path>",
      "size_mb": <size>,
      "age_days": <days since last_modified>,
      "retention_days": <retention>,
      "actions": ["rotate", "compress", "delete"]
    },
    ...
  ],
  "summary": {
    "total_files": 12,
    "files_to_rotate": <count>,
    "files_to_compress": <count>,
    "files_to_delete": <count>,
    "files_no_action": <count>
  }
}
```

7. The `files` array must include ALL files from the inventory.
8. Files that need no action should have an empty `actions` array.

## Output

Save the rotation plan to `workspace/rotation_plan.json`.
