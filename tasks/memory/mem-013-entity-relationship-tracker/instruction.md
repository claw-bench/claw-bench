# Task: Entity Relationship Tracker

Read the event stream in `workspace/events.jsonl`. Each line is a JSON object describing an event that changes relationships between people and teams.

Event types:
- `join`: A person joins a team. `{"type": "join", "person": "X", "team": "T"}`
- `leave`: A person leaves a team. `{"type": "leave", "person": "X", "team": "T"}`
- `merge`: Two teams merge into one. All members of the source team move to the target team and the source team is dissolved. `{"type": "merge", "source_team": "S", "target_team": "T"}`
- `promote`: A person becomes the lead of their team. `{"type": "promote", "person": "X", "team": "T"}`

Your job:

1. Read all events in order and process them sequentially.
2. Track the current state of all entities after all events are processed.
3. Produce `workspace/entity_graph.json` with this structure:

```json
{
  "teams": {
    "<team_name>": {
      "members": ["<person>", ...],
      "lead": "<person or null>",
      "active": true/false
    }
  },
  "people": {
    "<person_name>": {
      "current_team": "<team or null>",
      "history": ["<team1>", "<team2>", ...]
    }
  },
  "dissolved_teams": ["<team_name>", ...],
  "total_events": <int>
}
```

- `members` lists should be sorted alphabetically.
- `history` is the ordered list of teams the person was on (including teams they left).
- `dissolved_teams` lists teams that were merged into other teams (sorted alphabetically).
- A person can only be on one team at a time.

## Output
- `workspace/entity_graph.json`
