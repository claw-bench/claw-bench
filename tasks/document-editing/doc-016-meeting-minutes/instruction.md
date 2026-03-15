# Task: Format Meeting Minutes from Raw Notes

You are given raw, unstructured meeting notes at `workspace/raw_notes.txt`. Transform them into properly formatted meeting minutes.

## Requirements

1. Read `workspace/raw_notes.txt`.
2. Produce a well-formatted Markdown document with the following sections:

### Header
- A top-level heading with the meeting title (e.g., "Product Review Meeting")
- The meeting date formatted properly (e.g., "March 10, 2026")

### Attendees
- A section listing **Present** attendees
- A section listing **Absent** attendees (with reason if given)

### Discussion Summary
- A section summarizing the key discussion points raised by each participant

### Decisions
- A numbered list of all decisions made during the meeting

### Action Items
- A Markdown table with columns: **Person** | **Action** | **Due Date**
- Each action item from the notes should appear as a row

3. Write the result to `workspace/minutes.md`.

## Output

Save the formatted meeting minutes to `workspace/minutes.md`.
