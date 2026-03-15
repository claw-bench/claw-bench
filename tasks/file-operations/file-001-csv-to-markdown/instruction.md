# Task: Convert CSV to Markdown Table

You are given a CSV file at `workspace/sample.csv`. Convert it into a Markdown table.

## Requirements

1. Read `workspace/sample.csv`.
2. Produce a valid Markdown table with:
   - A header row matching the CSV column names.
   - A separator row using `---` for each column.
   - One data row per CSV record.
3. Write the result to `workspace/output.md`.

## Example

Given this CSV:

```
Name,Age
Alice,30
```

The output should be:

```markdown
| Name | Age |
| --- | --- |
| Alice | 30 |
```

## Output

Save the Markdown table to `workspace/output.md`.
