# Task: RSS Feed Parser

You are given an RSS feed file at `workspace/feed.xml`. Parse the feed and extract all items into a structured JSON file.

## Requirements

1. Read `workspace/feed.xml`.
2. Extract every `<item>` from the RSS feed.
3. For each item, extract:
   - `title` - The item's title text
   - `link` - The item's URL
   - `pubDate` - The publication date as a string (keep the original format from the XML)
   - `description` - The item's description text (strip any HTML tags, keep plain text only)
4. Sort items by publication date in **descending** order (newest first). Parse the RFC 2822 date format for sorting.
5. Write the result to `workspace/feed_items.json` as a JSON array of objects.

## Output Format

```json
[
  {
    "title": "Article Title",
    "link": "https://example.com/article",
    "pubDate": "Mon, 15 Sep 2024 14:30:00 GMT",
    "description": "Plain text description..."
  }
]
```

## Output

Save the JSON array to `workspace/feed_items.json`.
