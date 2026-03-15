# CSV Processing Skill

## Overview
This skill provides guidance on working with CSV (Comma-Separated Values) files,
including reading, parsing, transforming, and writing CSV data.

## Reading CSV Files

### Python Standard Library
Use the `csv` module for reliable CSV handling:

```python
import csv

with open("input.csv", "r", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        # row is an OrderedDict with column headers as keys
        process(row)
```

### Key Considerations
- Always specify `newline=""` when opening CSV files to avoid blank-row issues.
- Use `DictReader` when you need named column access; use `reader` for index-based access.
- Handle encoding explicitly with `encoding="utf-8"` (or detect with `chardet`).

## Parsing and Transformation

### Common Patterns
- **Filtering rows**: Iterate and apply conditions before collecting results.
- **Type conversion**: CSV values are always strings; cast numerics with `int()` / `float()`.
- **Handling missing values**: Check for empty strings and decide on a default or skip strategy.
- **Date parsing**: Use `datetime.strptime()` for consistent date formats.

### Delimiter Detection
Not all CSV files use commas. Use `csv.Sniffer` to auto-detect:

```python
with open("data.csv", "r") as f:
    dialect = csv.Sniffer().sniff(f.read(4096))
    f.seek(0)
    reader = csv.reader(f, dialect)
```

## Writing CSV Files

```python
import csv

with open("output.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["name", "age", "city"])
    writer.writeheader()
    writer.writerows(data)
```

### Formatting Tips
- When converting to other formats (Markdown, JSON), preserve column ordering.
- For Markdown tables, align columns and escape pipe characters within values.
- For JSON output, use `json.dumps()` with `indent` for readability.

## Error Handling
- Wrap I/O in try/except for `FileNotFoundError`, `csv.Error`, and `UnicodeDecodeError`.
- Validate expected columns exist before accessing them.
- Log malformed rows rather than failing the entire pipeline.
