# Task: Website Structure Mapping

Map the full structure of a website from its HTML files and detect broken links.

## Requirements

1. Read all HTML files in `workspace/site/` (10 HTML files).
2. For each page, extract all internal links (links to other pages within the site, identified by relative paths or same-domain absolute URLs).
3. Generate `workspace/sitemap.json` with:
   - `pages`: array of objects, each with:
     - `file`: filename.
     - `title`: page title from `<title>` tag.
     - `path`: the URL path (derived from filename, e.g., `index.html` -> `/`, `about.html` -> `/about`).
     - `links_to`: array of paths this page links to (internal only).
     - `linked_from`: array of paths that link to this page.
   - `total_pages`: number of pages.
   - `total_internal_links`: total number of internal links found.
4. Generate `workspace/broken_links.json` with:
   - `broken`: array of objects with `source_file`, `link_href`, and `reason` for links pointing to pages that do not exist in the site.
   - `total_broken`: count of broken links.

## Output

Save `workspace/sitemap.json` and `workspace/broken_links.json`.
