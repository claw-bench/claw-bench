#!/usr/bin/env bash
# Oracle solution for code-005-implement-stack
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

cat > "$WORKSPACE/stack.py" <<'PYTHON'
"""Stack data structure implementation."""


class Stack:
    """A LIFO stack."""

    def __init__(self):
        self._items = []

    def push(self, item):
        """Push an item onto the stack."""
        self._items.append(item)

    def pop(self):
        """Remove and return the top item."""
        if not self._items:
            raise IndexError("pop from empty stack")
        return self._items.pop()

    def peek(self):
        """Return the top item without removing it."""
        if not self._items:
            raise IndexError("peek at empty stack")
        return self._items[-1]

    def is_empty(self):
        """Return True if the stack is empty."""
        return len(self._items) == 0

    def size(self):
        """Return the number of items."""
        return len(self._items)
PYTHON

echo "Solution written to $WORKSPACE/stack.py"
