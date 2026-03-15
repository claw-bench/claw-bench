# Task: Communication Audit

Perform a comprehensive audit of communications across multiple channels.

## Requirements

1. Read all JSON files in `workspace/communications/` — there are 4 channel files (`slack.json`, `email.json`, `teams.json`, `discord.json`). Each contains an array of message objects with `from`, `to` (string or array), `timestamp`, `subject` (optional), `body`, and `channel` fields.
2. Generate `workspace/metrics.json` with:
   - `total_messages`: total across all channels.
   - `per_channel`: object mapping channel name to message count.
   - `per_user_sent`: object mapping usernames to number of messages sent.
   - `busiest_channel`: channel name with most messages.
   - `busiest_user`: user who sent the most messages.
   - `date_range`: object with `start` and `end` (earliest and latest timestamps).
   - `avg_messages_per_day`: average messages per day across the date range, rounded to 1 decimal.
   - `response_pairs`: number of messages that are replies (where `subject` starts with "Re:").
3. Generate `workspace/audit_report.md` with:
   - A title: `# Communication Audit Report`
   - A `## Summary` section with total messages, date range, and busiest channel/user.
   - A `## Channel Breakdown` section with a markdown table of channel, message count, and percentage of total.
   - A `## Top Senders` section listing top 5 senders by message count.

## Output

Save `workspace/metrics.json` and `workspace/audit_report.md`.
