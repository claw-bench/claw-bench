# Task: Auto-Reply Generator

Generate appropriate auto-replies for incoming emails based on a set of rules.

## Input

- `workspace/incoming.json` — a JSON array of 8 incoming email objects with fields: `id`, `from`, `subject`, `body`, `category`
- `workspace/rules.json` — a JSON array of 5 reply rules, each with: `rule_id`, `match_category`, `condition` (keyword or pattern to look for), `reply_template`, `tone`

## Requirements

1. For each incoming email, check if any rule matches based on:
   - The email's `category` matching the rule's `match_category`
   - The email's subject or body containing the rule's `condition` keyword
2. If a rule matches, generate a reply using the `reply_template` as a base, personalized with the sender's name (extracted from the `from` field)
3. If no rule matches, do NOT generate a reply for that email
4. Each reply should maintain the specified `tone` from the matching rule

## Output

Write the replies to `workspace/replies.json` as a JSON array:

```json
[
  {
    "email_id": 1,
    "rule_id": "R1",
    "to": "sender@example.com",
    "subject": "Re: Original Subject",
    "body": "The generated reply text"
  }
]
```

Only include entries for emails that matched a rule.
