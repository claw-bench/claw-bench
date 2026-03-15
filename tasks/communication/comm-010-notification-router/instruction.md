# Task: Notification Router

You are given two files in `workspace/`:

- `rules.yaml` - Notification routing rules
- `events.json` - An event log

Route each event to the correct notification channels based on the rules.

## Requirements

1. Read both input files.
2. For each event in `events.json`, find the **first** matching rule from `rules.yaml` (rules are evaluated in order).
3. A rule matches if **all** of its conditions are satisfied:
   - `event_type`: matches if the event's `type` equals the rule's `event_type`
   - `severity_gte`: matches if the event's `severity` is >= this value (severity scale: 1=low, 2=medium, 3=high, 4=critical)
   - `source_in`: matches if the event's `source` is in this list
   - `tag_contains`: matches if any of the event's `tags` are in this list
   - If a condition is not specified in a rule, it is considered automatically satisfied.
4. Produce `workspace/routed_notifications.json` containing an array of objects:

```json
[
  {
    "event_id": "string",
    "matched_rule": "rule name or null if no match",
    "channels": ["channel1", "channel2"],
    "priority": "string (from the matched rule, or 'default' if no match)"
  }
]
```

5. If no rule matches an event, set `matched_rule` to `null`, `channels` to `["log"]`, and `priority` to `"default"`.
6. Preserve the order of events from the input.
7. Write with 2-space indentation.

## Output

Save the result to `workspace/routed_notifications.json`.
