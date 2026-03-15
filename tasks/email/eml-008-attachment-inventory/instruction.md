# Task: Email Attachment Inventory

Scan a directory of email JSON files and compile a complete inventory of all attachments.

## Input

- `workspace/emails/` — a directory containing 10 email JSON files (`email_01.json` through `email_10.json`). Each email file is a JSON object with fields: `id`, `from`, `subject`, `date`, `attachments` (array of attachment objects with `filename`, `size_bytes`, `content_type`)

## Requirements

1. Read all 10 email files from the `workspace/emails/` directory
2. Extract attachment metadata from each email
3. Compile a complete inventory of all attachments

## Output

Write the inventory to `workspace/attachments.json` as a JSON array:

```json
[
  {
    "email_id": 1,
    "filename": "report.pdf",
    "size_bytes": 245000,
    "content_type": "application/pdf"
  }
]
```

Include all attachments found across all emails. Emails with no attachments should not generate entries.
