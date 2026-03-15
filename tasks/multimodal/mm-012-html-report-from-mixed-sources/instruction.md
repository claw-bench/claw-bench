# Task: HTML Report from Mixed Sources

You are given three files in `workspace/`:
- `text_summary.txt` — a plain-text executive summary
- `data_table.csv` — tabular data with headers
- `metadata.json` — report metadata (title, author, date, department)

Combine these into a single structured HTML report.

## Requirements

1. Read all three input files from `workspace/`.
2. Produce `workspace/combined_report.html` containing a valid HTML document.
3. The HTML must include:
   - A `<!DOCTYPE html>` declaration.
   - A `<title>` element using the `title` field from metadata.json.
   - A metadata section displaying author, date, and department from metadata.json.
   - A summary section containing the text from text_summary.txt wrapped in a `<p>` tag.
   - A data section with an HTML `<table>` generated from data_table.csv, including `<th>` header cells and `<td>` data cells.
4. The report should have clear section headings using `<h1>` or `<h2>` tags.

## Output

Save the result to `workspace/combined_report.html`.
