# Task: Extract Links from HTML

Extract all links from an HTML page and classify them.

## Requirements

1. Read `workspace/page.html`.
2. Extract all `<a>` tags and collect their `href` attributes and link text.
3. Classify each link as:
   - `internal`: links starting with `/` or containing `example.com`
   - `external`: all other http/https links
4. Produce `workspace/links.json` — a JSON object with:
   - `links`: array of objects with `url`, `text`, and `type` (internal/external).
   - `total_count`: total number of links.
   - `internal_count`: number of internal links.
   - `external_count`: number of external links.

## Output

Save the extracted links to `workspace/links.json`.
