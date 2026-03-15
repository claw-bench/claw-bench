# Task: Notification Dispatcher

You are given a stream of events and routing rules. Match events to notification channels.

## Requirements

1. Read `workspace/events.jsonl` which contains one JSON event per line, each with:
   - `id`: unique event identifier
   - `type`: event type (e.g., "deployment", "alert", "incident")
   - `severity`: one of "low", "medium", "high", "critical"
   - `source`: the system that produced the event
   - `message`: event description
2. Read `workspace/routing_rules.json` which contains an array of rules, each with:
   - `name`: rule name
   - `match`: conditions object with optional keys `type`, `severity`, `source`. Each value can be a string (exact match) or array of strings (match any).
   - `channels`: array of notification channel names to dispatch to
3. For each event, find ALL matching rules. A rule matches if all specified conditions in `match` are satisfied.
4. Produce `workspace/dispatch_log.jsonl` with one JSON line per event:
   ```json
   {"event_id": "E1", "matched_rules": ["rule_name"], "channels": ["email", "slack"]}
   ```
5. Channels should be deduplicated and sorted alphabetically.
6. If no rules match an event, `matched_rules` and `channels` should be empty arrays.

## Output

Save the dispatch log to `workspace/dispatch_log.jsonl`.
