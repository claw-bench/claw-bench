# Task: Chat Sentiment Analysis

You are given a chat log and keyword lists. Classify each message's sentiment and produce a per-user summary report.

## Requirements

1. Read `workspace/chat_log.jsonl` - one JSON object per line with fields: `user`, `text`, `timestamp`.
2. Read `workspace/keywords.json` - contains `positive` and `negative` arrays of keywords.
3. For each message, classify its sentiment:
   - Count how many **positive** keywords appear in the message text (case-insensitive).
   - Count how many **negative** keywords appear in the message text (case-insensitive).
   - If positive count > negative count: sentiment is `"positive"`.
   - If negative count > positive count: sentiment is `"negative"`.
   - Otherwise (tie or both zero): sentiment is `"neutral"`.
   - Match keywords as whole words (e.g., "great" should not match "greatest").
4. Produce `workspace/sentiment_report.json` with the following structure:
   ```json
   {
     "users": {
       "username": {
         "total_messages": 5,
         "positive": 2,
         "negative": 1,
         "neutral": 2
       }
     },
     "overall": {
       "total_messages": 20,
       "positive": 8,
       "negative": 5,
       "neutral": 7
     }
   }
   ```

## Output

Save the sentiment report to `workspace/sentiment_report.json`.
