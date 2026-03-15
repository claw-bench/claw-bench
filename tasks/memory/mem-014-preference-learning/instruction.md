# Task: Preference Learning

Read the interaction log in `workspace/interactions.jsonl`. Each line describes a user interaction with an item:

```json
{
  "id": <int>,
  "action": "<liked|disliked|rated>",
  "item": "<item name>",
  "category": "<category>",
  "rating": <number 1-5, only present for "rated" actions>
}
```

Your job:

1. Read all interactions in order.
2. For each category, compute a **preference score** (0.0 to 1.0):
   - `liked` = 1.0
   - `disliked` = 0.0
   - `rated` = (rating - 1) / 4   (maps 1-5 to 0.0-1.0)
   - Category score = average of all interaction scores in that category, rounded to 2 decimal places.
3. Determine the overall preference pattern:
   - Count total likes, dislikes, and ratings.
4. Recommend the top 3 categories (highest preference score). If tied, sort alphabetically.
5. Produce `workspace/user_profile.json`:

```json
{
  "category_scores": {
    "<category>": {
      "score": <float>,
      "interaction_count": <int>,
      "likes": <int>,
      "dislikes": <int>,
      "ratings": <int>
    }
  },
  "overall": {
    "total_interactions": <int>,
    "total_likes": <int>,
    "total_dislikes": <int>,
    "total_ratings": <int>
  },
  "recommended_categories": ["<cat1>", "<cat2>", "<cat3>"]
}
```

## Output
- `workspace/user_profile.json`
