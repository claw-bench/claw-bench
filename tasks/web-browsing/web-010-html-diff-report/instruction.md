# Task: HTML Diff Report

You are given two HTML files: `workspace/before.html` and `workspace/after.html`. Compare them and produce a structured diff report.

## Requirements

1. Read `workspace/before.html` and `workspace/after.html`.
2. Compare the two HTML documents and identify:
   - **Added elements**: Elements present in `after.html` but not in `before.html`
   - **Removed elements**: Elements present in `before.html` but not in `after.html`
   - **Modified elements**: Elements that exist in both but have changed (text content, attributes, etc.)
3. Produce `workspace/diff_report.json` with the following structure:

```json
{
  "added_elements": [
    {
      "tag": "div",
      "id": "new-section",
      "class": "highlight",
      "description": "New div with id 'new-section' containing promotional content"
    }
  ],
  "removed_elements": [
    {
      "tag": "p",
      "id": "",
      "class": "old-notice",
      "description": "Paragraph with class 'old-notice' removed"
    }
  ],
  "modified_elements": [
    {
      "tag": "h1",
      "id": "main-title",
      "class": "",
      "description": "Text changed from 'Old Title' to 'New Title'"
    }
  ]
}
```

## Rules for Element Matching

- Elements are matched primarily by their `id` attribute. If an element has no `id`, match by a combination of tag name and `class` attribute.
- For each element entry: `id` and `class` should be empty strings if the attribute is not present.
- The `description` field should briefly describe what changed (for modifications) or what the element contains (for additions/removals).
- Only report significant structural elements (ignore changes in whitespace-only text nodes).
- Report elements at the most specific level (if a `<li>` was added inside a `<ul>`, report the `<li>`, not the `<ul>`).

## Output

Save the diff report to `workspace/diff_report.json`.
