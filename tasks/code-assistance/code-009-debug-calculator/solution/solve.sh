#!/usr/bin/env bash
# Oracle solution for code-009-debug-calculator
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

cat > "$WORKSPACE/calculator.py" <<'PYTHON'
"""Calculator module with bugs fixed."""

import math


def factorial(n):
    """Compute the factorial of n."""
    if n == 0:
        return 1
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result


def power(base, exp):
    """Compute base raised to the power of exp (non-negative integer exp)."""
    result = 1
    for _ in range(exp):
        result *= base
    return result


def safe_sqrt(n):
    """Compute the square root of n, returning None for negative inputs."""
    if n < 0:
        return None
    return math.sqrt(n)
PYTHON

echo "Solution written to $WORKSPACE/calculator.py"
