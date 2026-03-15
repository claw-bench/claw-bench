# Task: Generate Markdown Table of Contents

You are given a markdown file at `workspace/document.md` that contains multiple heading levels (`##`, `###`, `####`). Generate a table of contents and produce a new file with the TOC inserted at the top.

## Requirements

1. Read `workspace/document.md`.
2. Parse all headings at levels `##`, `###`, and `####`.
3. Generate a table of contents where:
   - Each entry is a markdown link in the format `- [Heading Text](#heading-anchor)`
   - The anchor is the heading text lowercased, with spaces replaced by hyphens, and non-alphanumeric characters (except hyphens) removed.
   - `###` headings are indented with 2 spaces.
   - `####` headings are indented with 4 spaces.
4. Insert the TOC at the top of the file, preceded by `## Table of Contents` and followed by a blank line before the original content.
5. Write the result to `workspace/document_with_toc.md`.

## Example

Given:

```markdown
## Introduction
Some text.
### Background
More text.
```

The TOC section would be:

```markdown
## Table of Contents
- [Introduction](#introduction)
  - [Background](#background)

```

## Output

Save the result to `workspace/document_with_toc.md`.
