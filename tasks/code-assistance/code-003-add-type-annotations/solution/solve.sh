#!/usr/bin/env bash
# Oracle solution for code-003-add-type-annotations
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

cat > "$WORKSPACE/utils.py" <<'PYTHON'
"""Utility functions with type annotations."""

from typing import Optional


def clamp(value: float, minimum: float, maximum: float) -> float:
    """Clamp a value between minimum and maximum."""
    if value < minimum:
        return minimum
    if value > maximum:
        return maximum
    return value


def flatten(nested_list: list[list]) -> list:
    """Flatten a list of lists into a single list."""
    result = []
    for sublist in nested_list:
        for item in sublist:
            result.append(item)
    return result


def merge_dicts(base: dict, override: dict) -> dict:
    """Merge two dictionaries, with override taking precedence."""
    merged = dict(base)
    merged.update(override)
    return merged


def truncate(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to max_length, adding suffix if truncated."""
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def safe_divide(a: float, b: float, default: Optional[float] = None) -> Optional[float]:
    """Divide a by b, returning default if b is zero."""
    if b == 0:
        return default
    return a / b
PYTHON

echo "Solution written to $WORKSPACE/utils.py"
