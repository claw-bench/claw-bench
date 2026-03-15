# Task: Auto-Reply Generator

You are given two files in `workspace/`:

- `inbox.json` — a list of incoming emails, each with `id`, `from`, `to`, `subject`, `date`, and `body` fields.
- `rules.yaml` — a list of auto-reply rules, each with a `subject_pattern` (a case-insensitive substring to match against the email subject) and a `reply_template` (a string that may contain `{sender}`, `{subject}`, and `{date}` placeholders).

## Requirements

1. Read `workspace/inbox.json` and `workspace/rules.yaml`.
2. For each email in the inbox, check if any rule's `subject_pattern` matches the email's subject (case-insensitive substring match). Use the first matching rule.
3. If a rule matches, generate a reply by substituting placeholders in the `reply_template`:
   - `{sender}` -> the `from` field of the email
   - `{subject}` -> the `subject` field of the email
   - `{date}` -> the `date` field of the email
4. Produce `workspace/auto_replies.json` with the following structure:

```json
[
  {
    "original_id": "<email id>",
    "from": "<original sender>",
    "subject": "<original subject>",
    "matched_rule": "<subject_pattern that matched>",
    "reply_body": "<generated reply text>"
  }
]
```

5. Only include emails that matched a rule. Emails with no matching rule should be omitted.
6. The output list should be in the same order as the emails appear in `inbox.json`.

## Output

Save the JSON auto-replies to `workspace/auto_replies.json`.
