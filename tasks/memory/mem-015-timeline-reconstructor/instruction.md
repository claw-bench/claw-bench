# Task: Timeline Reconstructor

You have two files in your workspace:

- `workspace/fragments.json`: An array of text fragments, each describing an event with a relative time reference to another event.
- `workspace/anchors.json`: An array of known absolute dates for specific events.

Each fragment has:
```json
{
  "id": "<event_id>",
  "event": "<event description>",
  "reference": "<relative time expression>",
  "relative_to": "<event_id of the reference event>"
}
```

Each anchor has:
```json
{
  "event_id": "<event_id>",
  "date": "YYYY-MM-DD"
}
```

Your job:

1. Read both files.
2. Use the anchors as starting points and resolve all relative references to compute absolute dates for every event.
3. Relative references use these patterns:
   - "N days before EVENT" -> subtract N days
   - "N days after EVENT" -> add N days
   - "N weeks before EVENT" -> subtract N*7 days
   - "N weeks after EVENT" -> add N*7 days
   - "same day as EVENT" -> same date
4. Produce `workspace/timeline.json`:

```json
{
  "events": [
    {
      "id": "<event_id>",
      "event": "<description>",
      "date": "YYYY-MM-DD"
    }
  ],
  "total_events": <int>,
  "earliest_date": "YYYY-MM-DD",
  "latest_date": "YYYY-MM-DD"
}
```

The `events` list must be sorted chronologically (earliest first). If two events share the same date, sort by event ID alphabetically.

## Output
- `workspace/timeline.json`
