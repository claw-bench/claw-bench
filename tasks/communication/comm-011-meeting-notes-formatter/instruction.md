# Task: Meeting Notes Formatter

You are given a raw meeting transcript at `workspace/meeting.txt`. Parse it and produce structured meeting notes in JSON format.

## Requirements

1. Read `workspace/meeting.txt`.
2. Extract the following information:
   - **attendees**: A list of unique speaker names found in the transcript (speakers appear as "Name:" at the start of lines).
   - **action_items**: A list of strings, each being the text after "ACTION:" markers in the transcript.
   - **decisions**: A list of strings, each being the text after "DECISION:" markers in the transcript.
3. Produce a JSON file with this structure:
   ```json
   {
     "attendees": ["Name1", "Name2", ...],
     "action_items": ["item1", "item2", ...],
     "decisions": ["decision1", "decision2", ...]
   }
   ```
4. Attendees should be sorted alphabetically.
5. Action items and decisions should appear in the order they occur in the transcript.
6. Strip leading/trailing whitespace from extracted text.

## Output

Save the result to `workspace/meeting_notes.json`.
