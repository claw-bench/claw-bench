# Task: SEO Analysis

Analyze HTML files for common SEO issues.

## Requirements

1. Read all HTML files in `workspace/site/` (3 files).
2. Check each page for SEO issues:
   - **missing_meta_description**: Page lacks a `<meta name="description">` tag.
   - **title_too_short**: `<title>` content is less than 30 characters.
   - **missing_h1**: Page has no `<h1>` tag.
   - **multiple_h1**: Page has more than one `<h1>` tag.
   - **missing_alt**: `<img>` tags without `alt` attribute.
   - **missing_viewport**: No `<meta name="viewport">` tag.
   - **missing_canonical**: No `<link rel="canonical">` tag.
   - **empty_link**: `<a>` tags with empty or missing `href`.
   - **heading_skip**: Heading levels that skip (h1 to h3, etc.).
3. Produce `workspace/seo_report.json` with:
   - `pages`: array of page analysis objects, each with:
     - `file`: filename.
     - `title`: page title.
     - `has_meta_description`: boolean.
     - `has_viewport`: boolean.
     - `has_canonical`: boolean.
     - `h1_count`: number of h1 tags.
     - `issues`: array of issue strings.
   - `total_issues`: total across all pages.
   - `issue_summary`: object mapping issue category to count.

## Output

Save the report to `workspace/seo_report.json`.
