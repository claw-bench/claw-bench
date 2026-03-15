#!/usr/bin/env bash
# Oracle solution for code-008-implement-merge-sort
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

cat > "$WORKSPACE/sorting.py" <<'PYTHON'
"""Merge sort implementation."""


def merge_sort(items):
    """Sort items using merge sort, returning a new sorted list."""
    if len(items) <= 1:
        return list(items)

    mid = len(items) // 2
    left = merge_sort(items[:mid])
    right = merge_sort(items[mid:])
    return _merge(left, right)


def _merge(left, right):
    """Merge two sorted lists into one sorted list."""
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result
PYTHON

echo "Solution written to $WORKSPACE/sorting.py"
