# Task: Structured Diff Reporter

You are given two JSON files in `workspace/`:
- `before.json` — the original configuration
- `after.json` — the updated configuration

Compare them and produce a structured diff report.

## Requirements

1. Read `workspace/before.json` and `workspace/after.json`.
2. Produce `workspace/diff_report.json` containing a JSON object with:
   - `"additions"`: array of objects `{"path": "...", "value": ...}` for keys present in `after` but not in `before`.
   - `"removals"`: array of objects `{"path": "...", "value": ...}` for keys present in `before` but not in `after`.
   - `"modifications"`: array of objects `{"path": "...", "old_value": ..., "new_value": ...}` for keys present in both but with different values.
3. Paths should use dot notation for nested keys (e.g., `"database.host"`).
4. Only compare leaf values (strings, numbers, booleans, null). If a key maps to an object in both versions, recurse into it.
5. Sort each array alphabetically by path.
6. Write with 2-space indentation.

## Output

Save the result to `workspace/diff_report.json`.
