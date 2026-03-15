# Task: Event-Driven Workflow

Process a sequence of events through a rule engine and log all triggered actions.

## Input Files

- `workspace/events.json` — an array of 10 events, each with:
  - `"id"`: event identifier
  - `"type"`: event type (e.g., `"login"`, `"purchase"`, `"error"`, `"signup"`, `"logout"`)
  - `"severity"`: one of `"low"`, `"medium"`, `"high"`, `"critical"`
  - `"source"`: the source system
  - `"timestamp"`: ISO timestamp string

- `workspace/rules.json` — an array of 6 rules, each with:
  - `"id"`: rule identifier
  - `"name"`: rule name
  - `"condition"`: object with fields to match against (e.g., `{"type": "error", "severity": "critical"}`)
  - `"action"`: the action to trigger (e.g., `"send_alert"`, `"log_warning"`, `"notify_admin"`)

## Requirements

1. Read both files.
2. For each event (in order), check every rule. A rule matches if all fields in the rule's `condition` match the event's corresponding fields.
3. One event can trigger multiple rules.
4. Write `workspace/actions_log.json` — a JSON object with:
   - `"actions"`: array of triggered actions, each containing:
     - `"event_id"`: which event triggered this
     - `"rule_id"`: which rule matched
     - `"action"`: the action taken
     - `"rule_name"`: name of the rule
   - `"summary"`: object with:
     - `"total_events"`: 10
     - `"total_actions_triggered"`: count of all actions
     - `"events_with_no_match"`: count of events that matched no rules
     - `"most_triggered_rule"`: id of the rule triggered most often

## Output

Save results to `workspace/actions_log.json`.
