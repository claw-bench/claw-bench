# Task: Extract Links from HTML Page

You are given a static HTML file at `workspace/page.html`. Extract all hyperlinks from the page and classify each one.

## Requirements

1. Read `workspace/page.html`.
2. Find every `<a>` tag with an `href` attribute.
3. For each link, determine:
   - **url**: The value of the `href` attribute.
   - **text**: The visible text content of the link (stripped of whitespace).
   - **type**: One of:
     - `"anchor"` if the href starts with `#`
     - `"internal"` if the href starts with `/` or is a relative path (no `://`)
     - `"external"` if the href contains `://`
4. Produce a JSON array sorted by the order the links appear in the HTML.

## Output

Save the result as a JSON array to `workspace/links.json`.

Example entry:
```json
{"url": "https://example.com", "text": "Example", "type": "external"}
```
