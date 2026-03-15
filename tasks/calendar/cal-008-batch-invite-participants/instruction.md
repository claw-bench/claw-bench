# Task: Batch Invite Participants

You are given:
- `workspace/calendar.json` — a calendar with 5 meetings, some tagged `"team"`
- `workspace/contacts.json` — a list of 4 contacts to invite

Add all contacts from `contacts.json` to the `participants` list of every meeting that has `"team"` in its `tags` array. Do not add duplicate participants (if a contact is already a participant, skip them). Meetings without the `"team"` tag must remain unchanged.

## Output

Write the updated calendar to `workspace/updated_calendar.json` with the same structure as the input.
