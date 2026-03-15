# Task: Log Rotation Script

You are given a `workspace/logs/` directory containing a manifest file `log_manifest.json` that describes 10 log files with their metadata (name, size, last modified date, current rotation count).

## Requirements

1. Read `workspace/logs/log_manifest.json`.
2. Apply the following rotation rules:
   - **Size threshold**: Rotate any log file >= 100MB
   - **Age threshold**: Rotate any log file older than 7 days (based on `last_modified` field, current date is `2024-03-15`)
   - **Max rotations**: Keep at most 5 rotated copies (e.g., app.log.1 through app.log.5)
3. Generate two output files:

### workspace/rotation_plan.json

```json
{
  "current_date": "2024-03-15",
  "rules": {
    "size_threshold_mb": 100,
    "age_threshold_days": 7,
    "max_rotations": 5
  },
  "files_to_rotate": [
    {
      "name": "<filename>",
      "reason": "size|age|both",
      "size_mb": <size>,
      "age_days": <days>,
      "current_rotations": <n>,
      "action": "rotate|rotate_and_compress|skip_max_reached"
    },
    ...
  ],
  "files_to_skip": [
    {
      "name": "<filename>",
      "reason": "within_thresholds"
    },
    ...
  ],
  "summary": {
    "total_files": 10,
    "to_rotate": <count>,
    "to_skip": <count>,
    "space_to_free_mb": <estimated MB from rotation>
  }
}
```

### workspace/rotate.sh

A valid bash script that would perform the rotation. The script should:
- Start with `#!/usr/bin/env bash` and `set -euo pipefail`
- Include a comment header explaining what it does
- For each file to rotate: rename current file with `.1` suffix, shift existing rotations up, remove any beyond max
- Create a new empty log file after rotation
- Be syntactically valid bash (though it won't actually be executed)

## Output

Save `workspace/rotation_plan.json` and `workspace/rotate.sh`.
