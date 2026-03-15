# Task: Fact Extraction and Update

Read the fact stream in `workspace/updates.jsonl`. Each line is a JSON object with:
- `id`: sequential fact statement ID
- `subject`: the entity the fact is about
- `attribute`: the attribute being stated
- `value`: the value of that attribute
- `timestamp`: when the fact was stated

Some later statements **contradict or update** earlier ones for the same subject and attribute. When this happens, the later statement supersedes the earlier one.

Your job:

1. Read all fact statements in order.
2. For each unique (subject, attribute) pair, determine the **current** (latest) value.
3. Track which facts were updated (i.e., had their value changed by a later statement).
4. Produce `workspace/current_facts.json` with this structure:

```json
{
  "facts": [
    {
      "subject": "<entity>",
      "attribute": "<attribute>",
      "current_value": "<latest value>",
      "original_value": "<first value, if different from current>",
      "was_updated": <true/false>,
      "source_id": <id of the statement that established the current value>
    }
  ],
  "total_statements": <int>,
  "total_unique_facts": <int>,
  "total_updates": <int>
}
```

Sort facts by subject (alphabetically), then by attribute (alphabetically).

## Output
- `workspace/current_facts.json`
