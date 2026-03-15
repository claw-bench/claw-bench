# Task: Generate Sitemap from Linked HTML Pages

You are given a directory `workspace/pages/` containing 5 HTML files that link to each other. Analyze the link structure and produce a sitemap.

## Requirements

1. Read all `.html` files in `workspace/pages/`.
2. For each page, find all `<a>` tags whose `href` points to another file in the pages directory.
3. Produce `workspace/sitemap.json` as a JSON object where:
   - Each key is the filename (e.g., `"index.html"`)
   - Each value is a sorted list of filenames that page links to

Only include links to files that exist in the pages directory. Ignore external links, anchors, and links to non-existent files.

## Output

Save the result to `workspace/sitemap.json`.

Example:
```json
{
  "index.html": ["about.html", "products.html"],
  "about.html": ["index.html"]
}
```
