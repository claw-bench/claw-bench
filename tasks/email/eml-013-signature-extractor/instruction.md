# Task: Email Signature Extractor

You are given a file at `workspace/emails.txt` containing multiple emails separated by a line consisting solely of `---`.

Each email has the following structure:
- A header block with `From:`, `To:`, `Subject:`, and `Date:` lines
- A blank line separating the header from the body
- The body text
- A signature block that begins after `--` on its own line (the standard email signature delimiter)

## Requirements

1. Read `workspace/emails.txt`.
2. Parse each email and extract the sender's email address (from the `From:` header) and their signature block (everything after the `--` delimiter line, trimmed of leading/trailing whitespace).
3. If an email has no `--` signature delimiter, its signature should be an empty string `""`.
4. Produce `workspace/signatures.json` mapping each sender email address to their signature text.
5. If the same sender appears multiple times, use the signature from their most recent email (by position in the file, later = more recent).

```json
{
  "alice@example.com": "Alice Johnson\nSenior Engineer\nAcme Corp",
  "bob@example.com": ""
}
```

## Output

Save the JSON mapping to `workspace/signatures.json`.
