# Task: Draft Out-of-Office Replies

Given a set of incoming emails and an out-of-office configuration, draft personalized auto-reply emails for each incoming message.

## Input

- `workspace/ooo_config.json` — the out-of-office configuration
- `workspace/incoming/` — directory containing incoming email JSON files

The OOO config has this structure:
```json
{
  "name": "张明",
  "away_from": "2026-03-15",
  "return_date": "2026-03-22",
  "delegate": "li.wei@company.com",
  "delegate_name": "李伟",
  "custom_message": "I am currently on annual leave."
}
```

Each incoming email has this structure:
```json
{
  "from": "sender@example.com",
  "sender_name": "Jane Smith",
  "to": "zhang.ming@company.com",
  "subject": "Original Subject",
  "date": "2026-03-15",
  "body": "Email body..."
}
```

## Requirements

1. Read the OOO configuration from `workspace/ooo_config.json`
2. Read all incoming email JSON files from `workspace/incoming/`
3. For each incoming email, generate a personalized out-of-office reply
4. Each reply must:
   - Be addressed to the original sender's email address
   - Have a subject starting with "Re: " followed by the original subject
   - Include a personalized greeting using the sender's name
   - Mention the return date (March 22, 2026)
   - Include the delegate's contact information (li.wei@company.com) for urgent matters
   - Include the custom message from the OOO config

## Output

For each incoming email, write a reply JSON file to `workspace/replies/` named `reply_to_{sender_local_part}.json`, where `{sender_local_part}` is the part of the sender's email before the @ symbol.

Each reply file must have this structure:
```json
{
  "to": "sender@example.com",
  "subject": "Re: Original Subject",
  "body": "Dear Jane,\n\nThank you for your email. I am currently on annual leave.\n\nI will be back on March 22, 2026. For urgent matters, please contact 李伟 at li.wei@company.com.\n\nBest regards,\n张明"
}
```

The body text can vary in phrasing but must include:
- A greeting with the sender's name
- The return date (March 22 or 2026-03-22)
- The delegate contact (li.wei@company.com)
- The custom OOO message
