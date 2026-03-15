# Task: Complex Email Workflow

Process a batch of incoming emails through a multi-step workflow pipeline.

## Input

- `workspace/incoming_batch.json` — a JSON array of 25 email objects with: `id`, `from`, `subject`, `body`, `date`, `has_attachment`
- `workspace/routing_rules.json` — a JSON object defining routing rules for 6 departments, each with keyword patterns and priority weights

## Workflow Steps

1. **Classify** each email into one of: `urgent`, `normal`, `low`
   - Emails with words like "urgent", "critical", "ASAP", "immediately", "deadline" in subject or body are `urgent`
   - Emails with words like "FYI", "newsletter", "no action needed" are `low`
   - All others are `normal`

2. **Route** each email to the appropriate department based on `routing_rules.json`
   - Match keywords in the email subject and body against department keyword lists
   - If multiple departments match, use the one with more keyword matches
   - If no department matches, route to "general"

3. **Summarize** each email in one sentence (max 100 characters)

4. **Prioritize** — create a priority queue ordering:
   - First by classification: urgent > normal > low
   - Within the same classification, by date (earliest first)

## Output

Write two output files:

### `workspace/processed_batch.json`
```json
[
  {
    "id": 1,
    "classification": "urgent",
    "department": "engineering",
    "summary": "Request to fix critical production bug in payment system",
    "priority_rank": 1
  }
]
```

### `workspace/routing_report.md`
A markdown report with:
- Total emails processed count
- Breakdown by department (department name and count)
- Breakdown by classification (urgent/normal/low counts)
- List of urgent emails with their ID, subject, and assigned department
