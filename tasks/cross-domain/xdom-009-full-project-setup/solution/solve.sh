#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE/project/src/csv_tool" "$WORKSPACE/project/tests"

cat > "$WORKSPACE/project/README.md" <<'MD'
# CSV Tool

A Python command-line tool for reading, transforming, and outputting CSV data.

## Features

- Read CSV files with automatic header detection
- Filter rows based on column value conditions
- Select specific columns from the data
- Sort rows by a specified column
- Output as CSV, JSON, or formatted table

## Installation

```bash
pip install .
```

Or for development:

```bash
pip install -e .
```

## Usage

```bash
# Read a CSV file
csv-tool read data.csv

# Filter rows
csv-tool read data.csv --filter "status=active"

# Select columns
csv-tool read data.csv --columns name,email

# Sort by column
csv-tool read data.csv --sort-by name

# Output as JSON
csv-tool read data.csv --format json
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests with `pytest`
5. Submit a pull request
MD

cat > "$WORKSPACE/project/setup.py" <<'PYTHON'
"""Setup script for csv-tool."""

from setuptools import setup, find_packages

setup(
    name="csv-tool",
    version="0.1.0",
    description="A CLI tool for reading, transforming, and outputting CSV data",
    author="Jane Developer",
    author_email="jane@example.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=[],
    extras_require={
        "table": ["tabulate"],
    },
    entry_points={
        "console_scripts": [
            "csv-tool=csv_tool.cli:main",
        ],
    },
)
PYTHON

cat > "$WORKSPACE/project/.gitignore" <<'GI'
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
*.manifest
*.spec
pip-log.txt
pip-delete-this-directory.txt
.venv/
venv/
ENV/
.env
.idea/
.vscode/
*.swp
*.swo
.DS_Store
.pytest_cache/
htmlcov/
.coverage
GI

cat > "$WORKSPACE/project/ci.yml" <<'YML'
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install flake8
      - run: flake8 src/ tests/

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -e ".[table]" pytest
      - run: pytest tests/ -v
YML

cat > "$WORKSPACE/project/src/csv_tool/__init__.py" <<'PYTHON'
"""CSV Tool - A CLI tool for CSV data processing."""

__version__ = "0.1.0"
PYTHON

cat > "$WORKSPACE/project/src/csv_tool/cli.py" <<'PYTHON'
"""Command-line interface for csv-tool."""

import argparse
import sys
from typing import Optional

from csv_tool.reader import read_csv
from csv_tool.transformer import filter_rows, select_columns, sort_rows


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="csv-tool",
        description="Read, transform, and output CSV data",
    )
    subparsers = parser.add_subparsers(dest="command")

    read_parser = subparsers.add_parser("read", help="Read a CSV file")
    read_parser.add_argument("file", help="Path to the CSV file")
    read_parser.add_argument("--filter", dest="filter_expr", help="Filter expression (column=value)")
    read_parser.add_argument("--columns", help="Comma-separated column names to select")
    read_parser.add_argument("--sort-by", dest="sort_by", help="Column to sort by")
    read_parser.add_argument("--format", dest="output_format", default="csv",
                             choices=["csv", "json", "table"],
                             help="Output format (default: csv)")

    return parser


def main(argv: Optional[list] = None) -> int:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 1

    if args.command == "read":
        rows = read_csv(args.file)

        if args.filter_expr:
            column, value = args.filter_expr.split("=", 1)
            rows = filter_rows(rows, column.strip(), value.strip())

        if args.columns:
            columns = [c.strip() for c in args.columns.split(",")]
            rows = select_columns(rows, columns)

        if args.sort_by:
            rows = sort_rows(rows, args.sort_by)

        output_data(rows, args.output_format)

    return 0


def output_data(rows: list, fmt: str) -> None:
    """Output rows in the specified format."""
    import csv
    import json
    import io

    if not rows:
        return

    if fmt == "json":
        print(json.dumps(rows, indent=2))
    elif fmt == "csv":
        writer = csv.DictWriter(sys.stdout, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    elif fmt == "table":
        try:
            from tabulate import tabulate
            print(tabulate(rows, headers="keys", tablefmt="grid"))
        except ImportError:
            # Fallback: simple table
            headers = list(rows[0].keys())
            print("\t".join(headers))
            for row in rows:
                print("\t".join(str(row.get(h, "")) for h in headers))


if __name__ == "__main__":
    sys.exit(main())
PYTHON

cat > "$WORKSPACE/project/src/csv_tool/reader.py" <<'PYTHON'
"""CSV file reader module."""

import csv
from pathlib import Path
from typing import List, Dict


def read_csv(filepath: str) -> List[Dict[str, str]]:
    """Read a CSV file and return a list of dictionaries.

    Args:
        filepath: Path to the CSV file.

    Returns:
        List of dictionaries, one per row.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    rows: List[Dict[str, str]] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(dict(row))

    return rows


def detect_delimiter(filepath: str) -> str:
    """Detect the delimiter used in a CSV file.

    Args:
        filepath: Path to the CSV file.

    Returns:
        The detected delimiter character.
    """
    with open(filepath, newline="", encoding="utf-8") as f:
        sample = f.read(4096)
        sniffer = csv.Sniffer()
        dialect = sniffer.sniff(sample)
        return dialect.delimiter
PYTHON

cat > "$WORKSPACE/project/src/csv_tool/transformer.py" <<'PYTHON'
"""Data transformation functions."""

from typing import List, Dict, Optional


def filter_rows(rows: List[Dict], column: str, value: str) -> List[Dict]:
    """Filter rows where column equals value.

    Args:
        rows: List of row dictionaries.
        column: Column name to filter on.
        value: Value to match.

    Returns:
        Filtered list of rows.
    """
    return [row for row in rows if row.get(column) == value]


def select_columns(rows: List[Dict], columns: List[str]) -> List[Dict]:
    """Select specific columns from rows.

    Args:
        rows: List of row dictionaries.
        columns: Column names to keep.

    Returns:
        Rows with only the specified columns.
    """
    return [{col: row.get(col, "") for col in columns} for row in rows]


def sort_rows(rows: List[Dict], column: str, reverse: bool = False) -> List[Dict]:
    """Sort rows by a specified column.

    Args:
        rows: List of row dictionaries.
        column: Column name to sort by.
        reverse: Sort in descending order if True.

    Returns:
        Sorted list of rows.
    """
    return sorted(rows, key=lambda r: r.get(column, ""), reverse=reverse)
PYTHON

cat > "$WORKSPACE/project/tests/__init__.py" <<'PYTHON'
"""Tests for csv-tool."""
PYTHON

cat > "$WORKSPACE/project/tests/test_reader.py" <<'PYTHON'
"""Tests for the CSV reader module."""

import csv
import tempfile
from pathlib import Path

from csv_tool.reader import read_csv, detect_delimiter


def _create_csv(content: str) -> str:
    """Helper to create a temp CSV file."""
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False)
    tmp.write(content)
    tmp.close()
    return tmp.name


def test_read_csv_basic():
    """Test reading a basic CSV file."""
    path = _create_csv("name,age\nAlice,30\nBob,25\n")
    rows = read_csv(path)
    assert len(rows) == 2
    assert rows[0]["name"] == "Alice"
    assert rows[0]["age"] == "30"


def test_read_csv_empty_file():
    """Test reading a CSV with only headers."""
    path = _create_csv("name,age\n")
    rows = read_csv(path)
    assert len(rows) == 0


def test_read_csv_file_not_found():
    """Test that FileNotFoundError is raised for missing files."""
    raised = False
    try:
        read_csv("/nonexistent/path.csv")
    except FileNotFoundError:
        raised = True
    assert raised, "Expected FileNotFoundError for missing file"


def test_read_csv_preserves_all_columns():
    """Test that all columns are preserved."""
    path = _create_csv("a,b,c\n1,2,3\n")
    rows = read_csv(path)
    assert set(rows[0].keys()) == {"a", "b", "c"}
PYTHON

cat > "$WORKSPACE/project/tests/test_transformer.py" <<'PYTHON'
"""Tests for the transformer module."""

from csv_tool.transformer import filter_rows, select_columns, sort_rows


SAMPLE_DATA = [
    {"name": "Alice", "age": "30", "status": "active"},
    {"name": "Bob", "age": "25", "status": "inactive"},
    {"name": "Carol", "age": "35", "status": "active"},
]


def test_filter_rows_basic():
    """Test filtering rows by column value."""
    result = filter_rows(SAMPLE_DATA, "status", "active")
    assert len(result) == 2
    assert all(r["status"] == "active" for r in result)


def test_filter_rows_no_match():
    """Test filtering with no matching rows."""
    result = filter_rows(SAMPLE_DATA, "status", "deleted")
    assert len(result) == 0


def test_select_columns():
    """Test selecting specific columns."""
    result = select_columns(SAMPLE_DATA, ["name", "status"])
    assert len(result) == 3
    assert set(result[0].keys()) == {"name", "status"}
    assert "age" not in result[0]


def test_sort_rows_ascending():
    """Test sorting rows by a column."""
    result = sort_rows(SAMPLE_DATA, "name")
    assert result[0]["name"] == "Alice"
    assert result[1]["name"] == "Bob"
    assert result[2]["name"] == "Carol"


def test_sort_rows_descending():
    """Test sorting rows in descending order."""
    result = sort_rows(SAMPLE_DATA, "name", reverse=True)
    assert result[0]["name"] == "Carol"
    assert result[2]["name"] == "Alice"
PYTHON

echo "Solution written to $WORKSPACE/project/"
