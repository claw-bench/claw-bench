# Task: Aggregate Team Standup Updates

You are given individual standup reports from team members in `workspace/standups/`. Each file is a JSON object with the team member's name, date, completed items, in-progress items, and blockers.

## Requirements

1. Read all JSON files in `workspace/standups/`.
2. Produce a single aggregated summary at `workspace/team_summary.json` with the following structure:

### Fields

- `date`: the standup date (all reports share the same date)
- `team_size`: number of team members
- `total_completed`: total number of completed items across all members
- `total_in_progress`: total number of in-progress items across all members (count each item in each member's `doing` list)
- `total_blockers`: total number of blockers across all members
- `members`: a list of objects, one per team member, each with:
  - `name`: the member's name
  - `completed_count`: number of items in their `done` list
  - `blocked`: `true` if they have any blockers, `false` otherwise
- `dependencies`: a list of cross-team dependencies detected from blockers and in-progress items. Look for mentions of other team members' names in blockers or doing items. Each dependency has:
  - `from`: the person who has the dependency (needs something)
  - `to`: the person they depend on (mentioned in their blocker/doing)
  - `item`: brief description of what is needed
- `unresolved_blockers`: a list of all blocker strings, prefixed with the member's name (e.g., `"Alice: Waiting for Stripe API keys from Bob"`)

## Output

Save the result to `workspace/team_summary.json`.
