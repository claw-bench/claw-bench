# Task: Email to Calendar

You have a file `workspace/emails.json` containing 10 emails. Some of these are meeting invitations, while others are regular correspondence.

## Objective

1. Parse all emails in `workspace/emails.json`.
2. Identify which emails are meeting invitations (they contain a specific date, time, and list of participants for a meeting).
3. Extract the meeting details and write them to `workspace/calendar_entries.json`.

## Output Format

Write `workspace/calendar_entries.json` as a JSON array of meeting objects. Each meeting object must have:

```json
{
  "subject": "Meeting subject line",
  "date": "YYYY-MM-DD",
  "start_time": "HH:MM",
  "duration_minutes": 60,
  "participants": ["email1@example.com", "email2@example.com"],
  "organizer": "organizer@example.com"
}
```

- `date` must be in ISO format (YYYY-MM-DD).
- `start_time` must be in 24-hour format (HH:MM).
- `duration_minutes` must be an integer.
- `participants` must be a list of email addresses (excluding the organizer).
- `organizer` is the sender of the meeting invitation email.

Only include actual meeting invitations. Do not include regular emails.
