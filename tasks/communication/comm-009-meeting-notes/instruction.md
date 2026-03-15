# Task: Meeting Notes Extraction

You are given a raw meeting transcript at `workspace/transcript.txt`. Extract structured meeting notes from it.

## Requirements

1. Read `workspace/transcript.txt`.
2. Produce `workspace/notes.json` containing a JSON object with the following structure:

```json
{
  "meeting_title": "string",
  "date": "YYYY-MM-DD",
  "attendees": ["name1", "name2", ...],
  "action_items": [
    {
      "owner": "person name",
      "task": "description of what needs to be done",
      "deadline": "YYYY-MM-DD"
    }
  ],
  "decisions": ["decision 1", "decision 2", ...],
  "next_meeting": "YYYY-MM-DD"
}
```

3. Rules:
   - **attendees**: List all people who spoke or were explicitly mentioned as attending. Use full names as they appear in the transcript. Sort alphabetically by last name.
   - **action_items**: Extract every action item mentioned. Each must have an owner (the person responsible), a concise task description, and a deadline date. If a deadline is expressed as a relative date (e.g., "by next Friday"), compute the actual date based on the meeting date.
   - **decisions**: Extract key decisions that were agreed upon or finalized during the meeting. Each decision should be a concise statement.
   - **next_meeting**: The date of the next scheduled meeting.
   - **date**: The date the meeting took place.
   - **meeting_title**: The title or topic of the meeting as stated in the transcript.
4. Write with 2-space indentation.

## Output

Save the result to `workspace/notes.json`.
