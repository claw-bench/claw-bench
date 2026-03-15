# Task: Channel Activity Report

You are given channel message data. Analyze it and produce a CSV activity report.

## Requirements

1. Read `workspace/channels.json` which contains an array of channel objects. Each channel has:
   - `name`: channel name (string)
   - `messages`: array of message objects, each with `timestamp` (ISO 8601 format) and `author` (string)
2. For each channel, compute:
   - `channel_name`: the channel name
   - `total_messages`: total number of messages in the channel
   - `unique_authors`: count of distinct authors in the channel
   - `most_active_author`: the author with the most messages in that channel (if tie, pick alphabetically first)
   - `peak_hour`: the hour (0-23) with the most messages in that channel (if tie, pick the earliest hour)
3. Output a CSV file with columns: `channel_name,total_messages,unique_authors,most_active_author,peak_hour`
4. Rows should be sorted alphabetically by `channel_name`.
5. Include the header row.

## Output

Save the report to `workspace/activity_report.csv`.
