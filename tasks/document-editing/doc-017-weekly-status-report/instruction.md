# Task: Compile Weekly Status Report

You are given five daily standup log files in `workspace/standups/` (monday.txt through friday.txt). Each file contains sections for Done, In Progress, and Blockers. Aggregate these into a single weekly status report.

## Requirements

1. Read all five standup files from `workspace/standups/`.
2. Produce a JSON file with the following structure:

```json
{
  "week": "2026-03-09 to 2026-03-13",
  "completed": ["list of all completed items across the week"],
  "in_progress": ["items still in progress as of Friday"],
  "blockers": ["unresolved blockers as of Friday"],
  "completed_count": 8,
  "highlights": "Brief 1-2 sentence summary of the week's accomplishments"
}
```

### Rules
- **completed**: Collect all items from the "Done" sections across all five days. There should be 8 total completed items.
- **in_progress**: Use only the "In Progress" items from Friday's standup.
- **blockers**: Include only blockers that are still unresolved as of Friday (i.e., not marked "None" on that day).
- **completed_count**: Must equal the length of the completed array.
- **week**: Must be the date range "2026-03-09 to 2026-03-13".

3. Write the result to `workspace/weekly_report.json`.

## Output

Save the weekly status report to `workspace/weekly_report.json`.
