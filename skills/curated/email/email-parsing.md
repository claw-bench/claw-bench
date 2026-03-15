# Email Parsing Skill

## Overview
This skill covers extracting structured data from email messages, including
headers, body content, attachments, and metadata using Python's standard library.

## Parsing Raw Email Messages

### Using the email Module
```python
import email
from email import policy

with open("message.eml", "rb") as f:
    msg = email.message_from_binary_file(f, policy=policy.default)
subject, sender, date = msg["Subject"], msg["From"], msg["Date"]
```

### Extracting the Body
```python
def get_body(msg):
    """Return the plain-text body, falling back to HTML."""
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            if ctype == "text/plain":
                return part.get_content()
            if ctype == "text/html":
                return part.get_content()
    return msg.get_content()
```

## Header Analysis

- **Received chain**: Trace the delivery path by reading `Received` headers bottom-up.
- **Authentication results**: Check `DKIM-Signature`, `SPF`, and `ARC` headers for legitimacy.
- **Reply threading**: Use `Message-ID`, `In-Reply-To`, and `References` to reconstruct threads.

## Extracting Attachments

```python
for part in msg.iter_attachments():
    filename = part.get_filename()
    content = part.get_content()
    with open(filename, "wb") as f:
        f.write(content if isinstance(content, bytes) else content.encode())
```

## Parsing Structured Content from Bodies

- **Key-value extraction**: Use regex for forms like `Order ID: 12345`.
- **Table extraction**: Detect aligned whitespace or HTML `<table>` tags.
- **Link extraction**: Parse URLs with `re.findall(r'https?://\S+', body)`.

## Tips
- Always use `policy.default` for modern Unicode-aware parsing.
- Decode encoded headers with `email.header.decode_header` for non-ASCII subjects.
- Sanitize HTML bodies before processing to avoid injection from untrusted senders.
- Handle multipart/alternative by preferring `text/plain` over `text/html` when both exist.
- Store parsed results in a structured format (dict or dataclass) for downstream processing.
