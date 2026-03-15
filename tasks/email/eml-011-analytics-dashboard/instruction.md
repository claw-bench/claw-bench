# Task: Email Analytics Dashboard Data

Analyze an email archive and generate analytics data for a dashboard.

## Input

- `workspace/email_archive.json` — a JSON array of 100+ email objects spanning 3 months. Each email has: `id`, `from`, `to`, `subject`, `date` (ISO 8601), `in_reply_to` (message ID or null), `message_id`

## Requirements

Analyze the email archive and compute the following metrics:

1. **emails_per_day** — object mapping date strings (YYYY-MM-DD) to email counts
2. **response_times** — object with `average_minutes`, `median_minutes`, and `max_minutes` for emails that are replies (have `in_reply_to` set). Response time = time between the original email and its reply
3. **top_contacts** — array of the top 5 most frequent email addresses (from either `from` or `to` fields), sorted by frequency descending, each with `email` and `count`
4. **busiest_hours** — object mapping hour (0-23 as string) to email count, for all hours that have at least one email

## Output

Write the analytics to `workspace/analytics.json`:

```json
{
  "emails_per_day": {"2026-01-15": 3, "2026-01-16": 5},
  "response_times": {"average_minutes": 120, "median_minutes": 90, "max_minutes": 480},
  "top_contacts": [{"email": "alice@co.com", "count": 25}],
  "busiest_hours": {"9": 15, "10": 12}
}
```

All numeric values should be integers (round to nearest).
