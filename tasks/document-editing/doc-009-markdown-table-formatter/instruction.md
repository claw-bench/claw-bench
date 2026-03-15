# Task: Markdown Table Formatter

You are given a markdown file at `workspace/input.md` containing several tables with poor formatting: inconsistent column widths, missing or incorrect alignment markers, and irregular spacing.

## Requirements

1. Read `workspace/input.md`.
2. Produce `workspace/formatted.md` with all tables properly formatted:
   - Each column should have consistent width (padded with spaces so all rows in a column are the same width).
   - Columns that contain only numeric data (integers or decimals) in their data rows must be **right-aligned** (use `---:` in the separator row and right-pad values with leading spaces).
   - All other columns should be **left-aligned** (use `---` in the separator row).
   - Each cell should have exactly one space of padding on each side of the content (between the pipe and the content).
   - The separator row dashes should fill the full column width (matching the padded content width).
   - Non-table text (headings, paragraphs) must be preserved exactly as-is.
3. Write the result to `workspace/formatted.md`.

## Example

Given:

```
| Name|Age| Salary|
|---|---|---|
|Alice |30|50000.50 |
| Bob| 25 |62000|
```

The output should be:

```
| Name  |  Age |    Salary |
| ----- | ---: | --------: |
| Alice |   30 |  50000.50 |
| Bob   |   25 | 62000     |
```

Wait — since "Salary" has `50000.50` and `62000`, both numeric, the column is right-aligned. The exact padding ensures all cells in a column are the same width.

## Output

Save the formatted markdown to `workspace/formatted.md`.
