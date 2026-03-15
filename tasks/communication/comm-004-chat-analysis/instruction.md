# Task: Chat Log Analysis

You are given a chat log at `workspace/chat_log.json`. Analyze it and produce statistics.

## Requirements

1. Read `workspace/chat_log.json`. It contains an array of 50 message objects with `user`, `timestamp` (ISO 8601), and `text` fields.
2. Compute:
   - `message_counts`: object mapping each user to their total message count.
   - `hourly_activity`: object mapping hour (0-23, as strings) to message count for that hour.
   - `peak_hour`: the hour (integer) with the most messages.
   - `avg_response_time_seconds`: average time in seconds between consecutive messages (regardless of user). Round to the nearest integer.
   - `most_active_user`: the user with the most messages.
   - `total_messages`: total number of messages.
3. Write results to `workspace/chat_stats.json`.

## Output

Save the analysis to `workspace/chat_stats.json`.
