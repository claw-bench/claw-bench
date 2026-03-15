# Task: Meeting Notes Generator

You are given:
- `workspace/meeting.json` — details of an upcoming meeting including agenda items and references to past meetings
- `workspace/attendees.json` — profiles of all attendees with their roles and past action items

Generate a structured meeting preparation document at `workspace/prep_notes.md`.

## Required Sections

The markdown document must contain exactly these sections (use `## ` headers):

1. `## Meeting Overview` — Title, date, time, duration, and location from the meeting data
2. `## Attendees` — A bulleted list of each attendee with their name, role, and department
3. `## Agenda` — A numbered list of all agenda items from the meeting data
4. `## Previous Action Items` — A bulleted list of all unresolved action items from the attendees data, grouped by assignee name
5. `## References` — A bulleted list of past meeting references from the meeting data with their dates and titles

## Output

Write the preparation notes to `workspace/prep_notes.md`.
