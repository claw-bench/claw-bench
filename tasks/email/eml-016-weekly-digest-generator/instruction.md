# Task: Generate Weekly Email Digest

Analyze a week's worth of email JSON files and produce a structured weekly digest grouped by sender with urgency highlights.

## Input

- `workspace/emails/` — a directory containing 8 JSON email files from the past week

Each email file has this structure:
```json
{
  "from": "sender@example.com",
  "to": "you@company.com",
  "subject": "Email Subject",
  "date": "2026-03-XX",
  "body": "Email body text...",
  "read": true
}
```

## Requirements

1. Read all JSON email files from `workspace/emails/`
2. Group emails by sender address
3. Identify urgent emails: any email with "urgent" or "URGENT" (case-insensitive) in the subject line should be marked as urgent
4. Count total emails and total urgent emails
5. For each sender, list all their email subjects, their count, and whether any of their emails is urgent

## Output

Write the digest to `workspace/digest.json` with the following structure:

```json
{
  "period": "2026-03-06 to 2026-03-12",
  "total_emails": 8,
  "urgent_count": 2,
  "by_sender": [
    {
      "sender": "alice@company.com",
      "count": 3,
      "subjects": ["Q1 Report Draft", "URGENT: Budget Approval", "Team Lunch Friday"],
      "has_urgent": true
    }
  ]
}
```

Field specifications:
- `period` — string in format "YYYY-MM-DD to YYYY-MM-DD" covering the date range of the emails
- `total_emails` — integer, total number of emails processed
- `urgent_count` — integer, number of emails with "urgent" (case-insensitive) in the subject
- `by_sender` — array of objects, one per unique sender, sorted alphabetically by sender address
- Each sender object contains:
  - `sender` — the sender's email address
  - `count` — integer, number of emails from this sender
  - `subjects` — array of subject strings from this sender's emails
  - `has_urgent` — boolean, true if any email from this sender has "urgent" in the subject
