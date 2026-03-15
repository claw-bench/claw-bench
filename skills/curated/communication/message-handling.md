# Message Handling Skill

## Overview
This skill provides guidance on cross-channel message processing including
formatting, contact management, chat analytics, and notification routing.

## Cross-Channel Message Formatting

### Normalization Strategy
Messages from different channels (email, chat, SMS, webhook) arrive in different
formats. Normalize them into a common structure before processing:

```python
def normalize_message(raw, channel):
    """Convert channel-specific message to a common format."""
    return {
        "id": raw.get("id") or generate_id(),
        "channel": channel,
        "sender": extract_sender(raw, channel),
        "recipients": extract_recipients(raw, channel),
        "subject": raw.get("subject", ""),
        "body": extract_body(raw, channel),
        "timestamp": parse_timestamp(raw, channel),
        "attachments": extract_attachments(raw, channel),
        "metadata": extract_metadata(raw, channel),
    }
```

### Format Conversion
When relaying messages across channels, adapt formatting:
- **Markdown to plain text**: Strip formatting markers, preserve structure with
  indentation and line breaks.
- **HTML to plain text**: Remove tags, preserve link URLs in parentheses,
  convert lists to bulleted lines.
- **Plain text to Markdown**: Detect URLs and wrap in links, preserve
  code-like content in backticks.

```python
import re

def html_to_plain(html):
    """Basic HTML to plain text conversion."""
    text = re.sub(r"<br\s*/?>", "\n", html)
    text = re.sub(r"<p>", "\n", text)
    text = re.sub(r"<a\s+href=['\"]([^'\"]+)['\"][^>]*>([^<]+)</a>",
                  r"\2 (\1)", text)
    text = re.sub(r"<li>", "- ", text)
    text = re.sub(r"<[^>]+>", "", text)
    return text.strip()
```

### Character Limit Handling
Different channels have different limits (SMS: 160, tweet: 280, etc.):
1. Measure the message length against the target limit.
2. If over limit, truncate at the last word boundary before the limit.
3. Append an ellipsis or a "continued" indicator.
4. For critical content, split into multiple messages with sequence markers.

## Contact Deduplication

### Matching Strategies
Contacts from different sources often overlap. Use multi-field matching:

```python
def normalize_for_matching(value):
    """Normalize a string for fuzzy matching."""
    return re.sub(r"[^a-z0-9]", "", value.lower())

def contacts_match(a, b, threshold=0.8):
    """Check if two contacts likely refer to the same person."""
    # Exact email match is definitive
    if a.get("email") and a["email"].lower() == b.get("email", "").lower():
        return True

    # Exact phone match (after normalization)
    a_phone = re.sub(r"[^\d]", "", a.get("phone", ""))
    b_phone = re.sub(r"[^\d]", "", b.get("phone", ""))
    if a_phone and a_phone == b_phone:
        return True

    # Name similarity as a secondary signal
    a_name = normalize_for_matching(a.get("name", ""))
    b_name = normalize_for_matching(b.get("name", ""))
    if a_name and b_name:
        similarity = compute_similarity(a_name, b_name)
        return similarity >= threshold

    return False
```

### Merge Strategy
When duplicates are found:
1. Choose one record as the primary (prefer the most complete record).
2. Fill missing fields from the secondary record.
3. For conflicting fields, prefer the most recently updated value.
4. Maintain a link to all source records for traceability.

### Phone Number Normalization
```python
def normalize_phone(phone):
    """Strip formatting and ensure consistent phone representation."""
    digits = re.sub(r"[^\d+]", "", phone)
    # Add country code if missing (assuming US)
    if len(digits) == 10:
        digits = "+1" + digits
    elif len(digits) == 11 and digits.startswith("1"):
        digits = "+" + digits
    return digits
```

## Chat Analytics

### Response Time Analysis
```python
from datetime import datetime

def calculate_response_times(messages):
    """Calculate response times between consecutive messages in a thread."""
    sorted_msgs = sorted(messages, key=lambda m: m["timestamp"])
    response_times = []

    for i in range(1, len(sorted_msgs)):
        if sorted_msgs[i]["sender"] != sorted_msgs[i - 1]["sender"]:
            delta = sorted_msgs[i]["timestamp"] - sorted_msgs[i - 1]["timestamp"]
            response_times.append({
                "responder": sorted_msgs[i]["sender"],
                "seconds": delta.total_seconds(),
            })

    return response_times
```

### Activity Pattern Detection
- **Peak hours**: Bucket messages by hour-of-day to find activity peaks.
- **Active participants**: Count messages per sender for engagement ranking.
- **Thread depth**: Measure reply chain length for conversation complexity.
- **Message frequency**: Track messages per day/week for trend analysis.

```python
from collections import Counter

def activity_by_hour(messages):
    """Count messages per hour of day."""
    hours = Counter(m["timestamp"].hour for m in messages)
    return dict(sorted(hours.items()))

def top_participants(messages, n=10):
    """Return the most active participants."""
    senders = Counter(m["sender"] for m in messages)
    return senders.most_common(n)
```

## Notification Routing

### Priority-Based Routing
Route notifications based on urgency and recipient preferences:

```python
def route_notification(message, recipient_prefs):
    """Determine the best channel for a notification."""
    priority = message.get("priority", "normal")

    if priority == "critical":
        return recipient_prefs.get("critical_channel", "sms")
    elif priority == "high":
        return recipient_prefs.get("high_channel", "push")
    else:
        return recipient_prefs.get("default_channel", "email")
```

### Delivery Rules
- **Do-not-disturb windows**: Check recipient timezone and quiet hours.
- **Batching**: Low-priority notifications can be batched into digests.
- **Escalation**: If no acknowledgment within a timeout, escalate to the
  next channel (email -> push -> SMS -> phone call).
- **Deduplication**: Suppress duplicate notifications within a cooldown window.

## Best Practices
- Always normalize sender identifiers before comparison or storage.
- Use UTC timestamps internally; convert for display based on recipient locale.
- Handle encoding differences (UTF-8, ASCII) when bridging channels.
- Preserve original message format alongside any normalized version.
- Apply rate limiting per recipient and per channel independently.
- Log all routing decisions for debugging delivery issues.
- Test message formatting across channels to catch rendering differences.
