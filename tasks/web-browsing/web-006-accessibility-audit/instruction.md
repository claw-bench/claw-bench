# Task: Accessibility Audit

Check HTML files for common accessibility issues.

## Requirements

1. Read all HTML files in `workspace/site/` (3 files).
2. Check for these accessibility issues:
   - **missing_alt**: `<img>` tags without an `alt` attribute (empty alt="" is acceptable for decorative images but should be noted).
   - **missing_label**: Form `<input>`, `<select>`, `<textarea>` without an associated `<label>` (matched by `for`/`id`).
   - **empty_link**: `<a>` tags with no text content.
   - **missing_lang**: `<html>` tag without a `lang` attribute.
   - **skipped_heading**: Heading levels that skip (e.g., h1 followed by h3, skipping h2).
   - **missing_table_header**: `<table>` without `<th>` elements.
   - **no_alt_video**: `<video>` without text alternative or `<track>` element.
   - **clickable_div**: `<div>` with `onclick` but no `role` or `tabindex`.
3. Produce `workspace/accessibility_report.json` with:
   - `issues`: array of objects, each with `file`, `category` (from above list), `element`, and `description`.
   - `summary`: object mapping each category to its count.
   - `files_scanned`: number of files checked.
   - `total_issues`: total issue count.

## Output

Save the report to `workspace/accessibility_report.json`.
