#!/usr/bin/env bash
# Oracle solution for code-006-refactor-comprehensions
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

cat > "$WORKSPACE/process.py" <<'PYTHON'
"""Data processing functions using list comprehensions."""


def get_even_numbers(numbers):
    """Return a list of even numbers from the input list."""
    return [n for n in numbers if n % 2 == 0]


def get_uppercased(strings):
    """Return a list of uppercased strings."""
    return [s.upper() for s in strings]


def get_lengths(strings):
    """Return a list of string lengths."""
    return [len(s) for s in strings]


def filter_positive(numbers):
    """Return only positive numbers from the input list."""
    return [n for n in numbers if n > 0]
PYTHON

echo "Solution written to $WORKSPACE/process.py"
