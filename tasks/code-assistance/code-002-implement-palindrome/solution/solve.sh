#!/usr/bin/env bash
# Oracle solution for code-002-implement-palindrome
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

cat > "$WORKSPACE/palindrome.py" <<'PYTHON'
"""Palindrome checker module."""


def is_palindrome(s: str) -> bool:
    """Check whether a string is a palindrome.

    Ignores case and non-alphanumeric characters.
    """
    cleaned = "".join(ch.lower() for ch in s if ch.isalnum())
    return cleaned == cleaned[::-1]
PYTHON

echo "Solution written to $WORKSPACE/palindrome.py"
