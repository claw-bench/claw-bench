# Task: Multi-Document Merge

Merge multiple markdown chapter files into a single cohesive book.

## Requirements

1. Read all markdown files in `workspace/chapters/` (chapter-01.md through chapter-05.md).
2. Merge them into `workspace/book.md` with:
   - A title: `# Complete Guide` at the top.
   - A `## Table of Contents` section listing all chapters and their sub-sections with proper numbering (e.g., `1. Introduction`, `   1.1 Background`).
   - A page break marker (`---`) between each chapter.
   - Consistent heading levels: each chapter's top heading should be `##`, sub-headings `###`, etc. (adjust levels if necessary).
   - Chapters ordered by their filename number (01, 02, 03, 04, 05).
3. All content from all chapters must be preserved.

## Output

Save the merged book to `workspace/book.md`.
