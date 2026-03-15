# Task: Thread Reconstruction

Reconstruct email threads from a flat list of unordered individual emails.

## Input

- `workspace/flat_emails.json` — a JSON array of 20 email objects in random order. Each email has:
  - `id` — unique numeric identifier
  - `message_id` — unique message ID string (e.g., `"msg-001"`)
  - `in_reply_to` — the `message_id` of the parent email, or `null` if it starts a thread
  - `from`, `to`, `subject`, `date`, `body`

## Requirements

1. Group emails into threads based on their `message_id` and `in_reply_to` references
2. Each thread starts with an email where `in_reply_to` is `null`
3. Order messages within each thread chronologically by date
4. Sort threads by the date of the first message in each thread (earliest first)

## Output

Write the reconstructed threads to `workspace/threads.json` as a JSON array of thread objects:

```json
[
  {
    "thread_id": 1,
    "subject": "Original subject of first email",
    "message_count": 5,
    "messages": [
      {"id": 1, "message_id": "msg-001", "from": "...", "date": "...", "body": "..."},
      {"id": 3, "message_id": "msg-003", "from": "...", "date": "...", "body": "..."}
    ]
  }
]
```

Each thread must include `thread_id` (sequential starting from 1), `subject` (from the first message), `message_count`, and `messages` (ordered chronologically).
