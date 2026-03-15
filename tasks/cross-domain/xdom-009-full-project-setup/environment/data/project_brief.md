# Project Brief: CSV Tool

## Overview

We need a Python command-line tool called `csv-tool` that reads, transforms, and outputs CSV data. It should be installable via pip and provide a `csv-tool` command.

## Features

1. **Read CSV**: Read CSV files with automatic header detection
2. **Filter Rows**: Filter rows based on column value conditions
3. **Select Columns**: Select specific columns from the data
4. **Sort**: Sort rows by a specified column
5. **Output Formats**: Output as CSV, JSON, or formatted table

## Technical Requirements

- Python 3.9+
- Use `argparse` for CLI argument parsing
- Use only standard library (no external dependencies for core functionality)
- Include `tabulate` as optional dependency for table formatting
- Follow PEP 8 style guidelines
- Include type hints

## CLI Usage Examples

```bash
csv-tool read data.csv
csv-tool read data.csv --filter "status=active"
csv-tool read data.csv --columns name,email
csv-tool read data.csv --sort-by name
csv-tool read data.csv --format json
```

## Author

Jane Developer (jane@example.com)

## Version

Start at version 0.1.0
