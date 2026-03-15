#!/usr/bin/env bash
# Oracle solution for code-015-performance-optimization
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

cat > "$WORKSPACE/slow.py" <<'PYTHON'
"""Optimized implementations."""

from functools import lru_cache


def find_duplicates(items):
    """Find all duplicate values in a list.

    Returns a sorted list of values that appear more than once.
    """
    seen = set()
    duplicates = set()
    for item in items:
        if item in seen:
            duplicates.add(item)
        seen.add(item)
    return sorted(duplicates)


def count_words(text):
    """Count the frequency of each word in the text.

    Returns a dict mapping word (lowercased) to count.
    """
    import string
    table = str.maketrans("", "", string.punctuation)
    words = text.lower().translate(table).split()
    result = {}
    for word in words:
        if word:
            result[word] = result.get(word, 0) + 1
    return result


def fibonacci(n):
    """Compute the nth Fibonacci number (0-indexed)."""
    if n <= 0:
        return 0
    if n == 1:
        return 1
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b
PYTHON

echo "Solution written to $WORKSPACE/slow.py"
