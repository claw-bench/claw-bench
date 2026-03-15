# Calendar Scheduling Skill

## Overview
This skill provides guidance on calendar operations including date/time handling,
timezone conversion, recurrence patterns, and conflict detection.

## Date and Time Handling

### Parsing Dates
Always parse dates into structured objects before manipulation:

```python
from datetime import datetime, date, time, timedelta

# Parse common formats
dt = datetime.strptime("2024-03-15 14:30", "%Y-%m-%d %H:%M")
dt = datetime.strptime("March 15, 2024", "%B %d, %Y")
dt = datetime.strptime("15/03/2024 2:30 PM", "%d/%m/%Y %I:%M %p")

# ISO 8601 parsing
dt = datetime.fromisoformat("2024-03-15T14:30:00+00:00")
```

### Key Format Codes
- `%Y`: 4-digit year, `%m`: zero-padded month, `%d`: zero-padded day
- `%H`: 24-hour hour, `%I`: 12-hour hour, `%M`: minute, `%p`: AM/PM
- `%A`: full weekday name, `%B`: full month name
- `%z`: UTC offset, `%Z`: timezone name

### Duration Arithmetic
```python
from datetime import timedelta

meeting_start = datetime(2024, 3, 15, 14, 0)
meeting_end = meeting_start + timedelta(hours=1, minutes=30)

# Calculate gap between events
gap = next_event_start - meeting_end
gap_minutes = gap.total_seconds() / 60
```

## Timezone Handling

### Best Practices
- Store all times internally as UTC; convert only for display.
- Use `zoneinfo` (Python 3.9+) or `pytz` for timezone operations.
- Never do arithmetic on naive datetimes that represent local times.

```python
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

# Create timezone-aware datetime
utc_now = datetime.now(timezone.utc)
eastern = utc_now.astimezone(ZoneInfo("America/New_York"))
tokyo = utc_now.astimezone(ZoneInfo("Asia/Tokyo"))

# Convert between timezones
local_dt = datetime(2024, 3, 15, 9, 0, tzinfo=ZoneInfo("US/Pacific"))
utc_dt = local_dt.astimezone(timezone.utc)
```

### DST Awareness
- Daylight saving transitions can cause ambiguous or nonexistent times.
- When scheduling recurring events, anchor to the wall-clock time in the
  target timezone rather than a fixed UTC offset.

## Recurrence Patterns

### Algorithm for Expanding Recurrences
1. Parse the recurrence rule (frequency, interval, count/until, exceptions).
2. Generate candidate occurrences by stepping forward from the start date.
3. Filter out exceptions (deleted or modified instances).
4. Stop when the count is reached or the until-date is exceeded.

### Common Frequencies
- **Daily**: Add N days per interval.
- **Weekly**: Add N weeks; filter by specified days of the week.
- **Monthly**: Anchor to day-of-month (clamp to month length) or to
  ordinal weekday (e.g., "second Tuesday").
- **Yearly**: Same month and day; handle Feb 29 by clamping to Feb 28.

```python
def expand_weekly(start, interval, days_of_week, until):
    """Generate weekly recurrence dates."""
    current = start
    while current <= until:
        if current.strftime("%A") in days_of_week:
            yield current
        current += timedelta(days=1)
        # Skip ahead after completing a week cycle
        if (current - start).days % (7 * interval) == 0:
            pass  # continue normally
```

### Edge Cases
- Month-end anchoring: if the event is on the 31st, months with fewer days
  should use the last day of that month.
- Timezone changes: recurring events should recalculate UTC offsets for
  each occurrence individually.

## Conflict Detection

### Interval Overlap Algorithm
Two events conflict if and only if each starts before the other ends:

```python
def events_overlap(start_a, end_a, start_b, end_b):
    """Return True if two time intervals overlap."""
    return start_a < end_b and start_b < end_a
```

### Finding All Conflicts
1. Sort events by start time.
2. Iterate with a sweep-line: maintain the latest end-time seen.
3. If the current event starts before that end-time, record a conflict.

```python
def find_conflicts(events):
    """Return pairs of conflicting events from a sorted list."""
    sorted_events = sorted(events, key=lambda e: e["start"])
    conflicts = []
    for i in range(len(sorted_events)):
        for j in range(i + 1, len(sorted_events)):
            if sorted_events[j]["start"] >= sorted_events[i]["end"]:
                break  # no further conflicts with event i
            conflicts.append((sorted_events[i], sorted_events[j]))
    return conflicts
```

### Free-Slot Discovery
1. Collect all busy intervals within the target window.
2. Merge overlapping intervals.
3. The gaps between merged intervals are the free slots.
4. Filter free slots by minimum required duration.

## Validation Checklist
- Verify that end time is strictly after start time.
- Check that dates are valid (no Feb 30, etc.).
- Confirm timezone identifiers are recognized IANA names.
- Validate recurrence rules terminate (have a count or until bound).
- Ensure all-day events span exactly midnight-to-midnight boundaries.

## Best Practices
- Represent times as ISO 8601 strings in data exchange.
- When displaying times, always show the timezone or UTC offset.
- For multi-participant scheduling, convert all times to a common
  reference (UTC) before running conflict detection.
- Log both the original local time and the UTC equivalent for auditability.
- Treat all-day events and timed events as separate categories in overlap logic.
