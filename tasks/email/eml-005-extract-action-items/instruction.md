# Task: Extract Action Items from Email Thread

Parse a multi-message email thread and extract all action items mentioned.

## Input

- `workspace/email_thread.json` — a JSON array of email messages forming a conversation thread, ordered chronologically. Each message has: `from`, `to`, `date`, `subject`, `body`

## Requirements

1. Read through the entire email thread
2. Identify all action items (tasks that someone needs to do)
3. For each action item, extract:
   - `task` — description of what needs to be done
   - `assignee` — who is responsible (if mentioned), otherwise `null`
   - `deadline` — when it's due (if mentioned), otherwise `null`

## Output

Write the action items to `workspace/action_items.json` as a JSON array:

```json
[
  {
    "task": "Prepare the quarterly report",
    "assignee": "Bob",
    "deadline": "March 15"
  }
]
```

Extract all action items found in the thread.
