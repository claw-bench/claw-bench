# Task: Document Comparison

Compare two versions of a text document and produce a structured diff.

## Requirements

1. Read `workspace/v1.txt` and `workspace/v2.txt`.
2. Compare them line by line and identify changes.
3. Produce `workspace/changes.json` with:
   - `added`: array of objects with `line_number` (in v2) and `content` for lines present in v2 but not v1.
   - `removed`: array of objects with `line_number` (in v1) and `content` for lines present in v1 but not v2.
   - `modified`: array of objects with `line_number_v1`, `line_number_v2`, `old_content`, and `new_content` for lines that changed between versions.
   - `unchanged_count`: number of lines that are identical in both versions.
   - `summary`: object with `total_added`, `total_removed`, `total_modified`, and `total_unchanged` counts.

Use a standard diff algorithm approach (e.g., longest common subsequence) to correctly align the documents.

## Output

Save the comparison to `workspace/changes.json`.
