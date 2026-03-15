# Task: Multi-File Search and Report

You are given a directory of text files at `workspace/docs/`. Search for a specific pattern and generate a report.

## Requirements

1. Search all `.txt` files in `workspace/docs/` for the pattern `TODO`.
2. For each match, record:
   - The filename (just the name, not the full path)
   - The line number where the match occurs
   - The full text of the matching line (trimmed of leading/trailing whitespace)
3. Generate a Markdown report at `workspace/report.md` containing:
   - A heading `# TODO Search Report`
   - A summary line: `Found X matches across Y files.`
   - A Markdown table with columns: `| File | Line | Content |`
   - Rows sorted by filename (ascending), then by line number (ascending)

## Example Output

```markdown
# TODO Search Report

Found 3 matches across 2 files.

| File | Line | Content |
| --- | --- | --- |
| notes.txt | 5 | TODO: Review the API documentation |
| readme.txt | 12 | TODO: Add installation instructions |
| readme.txt | 25 | TODO: Write contributing guide |
```

## Output

Save the report to `workspace/report.md`.
