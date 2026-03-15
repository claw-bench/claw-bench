# Task: Message Thread Summarization

You are given a discussion thread at `workspace/thread.json`. Summarize it into structured output.

## Requirements

1. Read `workspace/thread.json` — an array of 20 message objects with `user`, `timestamp`, and `text`.
2. Analyze the conversation and produce `workspace/summary.json` with:
   - `participants`: array of unique usernames who participated, sorted alphabetically.
   - `key_decisions`: array of strings, each describing a decision made in the thread. Extract decisions indicated by agreement or explicit statements (look for phrases like "let's go with", "decided", "agreed", "we'll use").
   - `action_items`: array of objects with `assignee` and `task` fields, representing commitments made (look for phrases like "I will", "I'll handle", "I can do", "will take care of").
   - `topic`: a short string (under 80 chars) describing the main topic of the thread.
   - `message_count`: total number of messages (integer).
3. All participants must be listed. All clearly stated decisions and action items must be captured.

## Output

Save the summary to `workspace/summary.json`.
