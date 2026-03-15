# Task: Email Thread Reconstructor

You are given a file at `workspace/emails.json` containing an unordered list of email messages. Each message has the following fields:

- `id`: unique message identifier
- `from`: sender email address
- `to`: recipient email address (or comma-separated list)
- `subject`: email subject line
- `date`: ISO 8601 datetime string
- `in_reply_to`: the `id` of the message this is a reply to, or `null` if it is a new thread

## Requirements

1. Read `workspace/emails.json`.
2. Reconstruct conversation threads by grouping messages that belong to the same thread. A thread starts with a message where `in_reply_to` is `null`, and includes all messages that reply to it (directly or transitively).
3. For each thread, assign a `thread_id` equal to the `id` of the root message (the one with `in_reply_to` = `null`).
4. Produce `workspace/threads.json` with the following structure:

```json
[
  {
    "thread_id": "<root message id>",
    "subject": "<subject of the root message>",
    "message_count": <int>,
    "participants": ["email1@example.com", "email2@example.com"],
    "messages": [
      {
        "id": "<string>",
        "from": "<string>",
        "to": "<string>",
        "subject": "<string>",
        "date": "<string>"
      }
    ]
  }
]
```

5. The `participants` list should contain all unique email addresses (from both `from` and `to` fields) in the thread, sorted alphabetically.
6. The `messages` list within each thread should be sorted by `date` ascending.
7. The threads list should be sorted by the date of the root message, ascending.

## Output

Save the JSON threads to `workspace/threads.json`.
