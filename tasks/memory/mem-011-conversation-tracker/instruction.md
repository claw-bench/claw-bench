# Task: Conversation Tracker

Read the conversation log in `workspace/conversation.jsonl`. It contains a stream of messages from multiple speakers, each with a speaker name, text, timestamp, and message ID.

Some messages **reference earlier messages** by recalling information, quoting content, or responding to specific earlier points.

Your job:

1. Read all messages in order.
2. Identify which messages reference or recall information from earlier messages.
3. Produce `workspace/context_map.json` with the following structure:

```json
{
  "total_messages": <int>,
  "speakers": [<list of unique speaker names>],
  "references": [
    {
      "source_id": <int message id being referenced>,
      "referencing_id": <int message id that references the source>,
      "referencing_speaker": "<speaker name>",
      "context_type": "<one of: quote, recall, response, correction>"
    }
  ]
}
```

- `quote`: The message directly quotes or paraphrases earlier text.
- `recall`: The message brings up a fact or detail mentioned earlier.
- `response`: The message directly responds to an earlier point or question.
- `correction`: The message corrects information from an earlier message.

## Output
- `workspace/context_map.json`
