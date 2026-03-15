# Task: Announcement Generator

You are given a template file and recipient data. Generate personalized announcements for each recipient.

## Requirements

1. Read `workspace/template.txt` which contains a message with `{placeholders}`.
2. Read `workspace/data.json` which contains an array of recipient objects, each with fields matching the placeholder names.
3. For each recipient, replace all `{placeholders}` in the template with the corresponding values from the recipient data.
4. Save each personalized announcement as a separate `.txt` file in `workspace/announcements/` directory.
5. File naming: use the recipient's name in lowercase with spaces replaced by underscores, e.g., `john_doe.txt`.
6. Ensure no unreplaced `{placeholders}` remain in any output file.

## Input Files

- `workspace/template.txt` - Message template with `{name}`, `{role}`, `{date}`, `{event}` placeholders.
- `workspace/data.json` - JSON array of recipient objects.

## Output

Save personalized announcement files to `workspace/announcements/<name>.txt`.
