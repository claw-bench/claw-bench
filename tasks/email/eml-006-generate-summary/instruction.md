# Task: Generate Email Summary

Summarize a long email into a structured summary with key points, action status, and urgency assessment.

## Input

- `workspace/long_email.txt` — a long email (500+ words) that needs summarizing

## Requirements

1. Read and analyze the entire email
2. Extract the key points discussed
3. Determine if any action is required by the recipient
4. Assess the urgency level

## Output

Write the summary to `workspace/summary.json` with the following structure:

```json
{
  "key_points": [
    "First key point",
    "Second key point"
  ],
  "action_required": true,
  "urgency": "high"
}
```

Field specifications:
- `key_points` — array of strings, each a concise summary point (at least 3 points)
- `action_required` — boolean indicating whether the recipient needs to take action
- `urgency` — one of: `"low"`, `"medium"`, `"high"`
