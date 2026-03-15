# Email Processing Skill

## Overview
This skill provides guidance on email handling including header parsing,
thread reconstruction, MIME processing, and classification heuristics.

## Header Parsing

### RFC 822 Standard Headers
Key headers to extract and their purposes:

- **From**: Sender address (may include display name).
- **To / Cc / Bcc**: Recipient lists (comma-separated).
- **Subject**: Topic line; often prefixed with "Re:" or "Fwd:".
- **Date**: Timestamp in RFC 2822 format.
- **Message-ID**: Globally unique identifier for the message.
- **In-Reply-To**: Message-ID of the direct parent message.
- **References**: Space-separated list of ancestor Message-IDs.

### Python Parsing
```python
import email
from email import policy

with open("message.eml", "rb") as f:
    msg = email.message_from_binary_file(f, policy=policy.default)

sender = msg["From"]
subject = msg["Subject"]
date = msg["Date"]
message_id = msg["Message-ID"]
in_reply_to = msg["In-Reply-To"]
references = msg["References"]
```

### Address Extraction
```python
from email.utils import parseaddr, getaddresses

# Single address
name, addr = parseaddr("Alice <alice@example.com>")

# Multiple addresses from To/Cc
recipients = getaddresses([msg["To"], msg["Cc"] or ""])
for name, addr in recipients:
    print(f"{name} <{addr}>")
```

### Date Normalization
```python
from email.utils import parsedate_to_datetime

dt = parsedate_to_datetime(msg["Date"])
# Returns a timezone-aware datetime object
```

## Thread Reconstruction

### Algorithm
1. Index all messages by their Message-ID.
2. For each message, use In-Reply-To to find its direct parent.
3. Fall back to the References header (last entry is the direct parent).
4. If neither header is present, use subject-based grouping:
   strip "Re:", "Fwd:", and prefixes, then group by normalized subject.
5. Build a tree structure with root messages at the top.

```python
from collections import defaultdict

def build_threads(messages):
    """Group messages into conversation threads."""
    by_id = {m["message_id"]: m for m in messages}
    children = defaultdict(list)
    roots = []

    for m in messages:
        parent_id = m.get("in_reply_to")
        if not parent_id and m.get("references"):
            parent_id = m["references"].split()[-1]
        if parent_id and parent_id in by_id:
            children[parent_id].append(m)
        else:
            roots.append(m)

    return roots, children
```

### Subject Normalization
```python
import re

def normalize_subject(subject):
    """Strip reply/forward prefixes for thread grouping."""
    pattern = r"^(Re|Fwd|Fw)\s*:\s*"
    cleaned = subject
    while re.match(pattern, cleaned, re.IGNORECASE):
        cleaned = re.sub(pattern, "", cleaned, count=1, flags=re.IGNORECASE)
    return cleaned.strip()
```

## MIME Types and Content Extraction

### Multipart Structure
Emails can contain nested MIME parts. Walk the structure to find content:

```python
def extract_body(msg):
    """Extract plain text body from an email message."""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                return part.get_content()
    else:
        return msg.get_content()
    return ""
```

### Common MIME Types
- `text/plain`: Plain text body (preferred for processing).
- `text/html`: HTML-formatted body (strip tags for text analysis).
- `multipart/mixed`: Message with attachments.
- `multipart/alternative`: Same content in multiple formats.
- `application/octet-stream`: Generic binary attachment.

### Attachment Handling
```python
def list_attachments(msg):
    """List all attachments with filenames and sizes."""
    attachments = []
    for part in msg.walk():
        if part.get_content_disposition() == "attachment":
            filename = part.get_filename() or "unnamed"
            payload = part.get_payload(decode=True)
            size = len(payload) if payload else 0
            attachments.append({"filename": filename, "size": size})
    return attachments
```

## Classification Heuristics

### Rule-Based Approaches
- **Keyword matching**: Check subject and body for category keywords.
- **Sender domain**: Group by organizational domain for business sorting.
- **Header flags**: Priority headers (X-Priority), auto-reply indicators.
- **Attachment presence**: Messages with attachments may need different routing.

### Spam Indicators
- Multiple recipients with no personalization.
- Mismatched From display name and actual address.
- Excessive use of HTML with few text alternatives.
- Presence of URL shorteners or suspicious domains.

### Priority Scoring
Assign points based on signals and sum for overall priority:
- Direct recipient (To): +2 points
- Cc recipient: +1 point
- From known contact: +2 points
- Contains action keywords ("urgent", "deadline", "ASAP"): +3 points
- Is a reply in an active thread: +1 point

## Filtering and Search

### Pattern Matching
```python
import re

def search_emails(messages, query):
    """Search messages by subject or body content."""
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    return [m for m in messages if
            pattern.search(m.get("subject", "")) or
            pattern.search(m.get("body", ""))]
```

### Date Range Filtering
```python
def filter_by_date(messages, start_date, end_date):
    """Filter messages within a date range."""
    return [m for m in messages
            if start_date <= m["date"] <= end_date]
```

## Best Practices
- Always handle encoding variations (UTF-8, Latin-1, etc.) when parsing.
- Preserve original headers for audit trails; work on parsed copies.
- When reconstructing threads, handle broken chains gracefully.
- Strip signatures and quoted text before analyzing body content.
- Use case-insensitive matching for header names per RFC 2822.
- Validate email addresses with a proper regex or library, not ad hoc checks.
