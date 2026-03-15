# Task: Format Message for Multiple Channels

You are given a message definition at `workspace/message.json`. Convert it into three different channel-specific formats.

## Requirements

1. Read `workspace/message.json`.
2. Create the directory `workspace/outputs/` and produce:
   - `workspace/outputs/telegram.txt` — plain text version with the subject as a bold header (`*Subject*`), followed by a blank line, then the body text, then a blank line, then each link on its own line formatted as `label: url`.
   - `workspace/outputs/slack.json` — a JSON object with a `"blocks"` array containing Slack Block Kit blocks: a header block with the subject, a section block with the body as markdown text, and a section block for each link with markdown `<url|label>`.
   - `workspace/outputs/email.txt` — an email-style format with `Subject: ...`, `From: ...`, `To: ...` headers (from the message JSON), a blank line, the body text, a blank line, then links each on a line as `label — url`.
3. All content (subject, body, sender, recipients, links) from the original message must be preserved in every format.

## Output

Save the three files into `workspace/outputs/`.
