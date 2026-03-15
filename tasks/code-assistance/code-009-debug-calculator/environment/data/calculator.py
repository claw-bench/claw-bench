"""Calculator module with three logical bugs."""

import math


def factorial(n):
    """Compute the factorial of n.

    Expected: factorial(5) == 120, factorial(0) == 1, factorial(1) == 1
    Bug: off-by-one in range causes incorrect result.
    """
    if n == 0:
        return 1
    result = 1
    for i in range(1, n):  # BUG: should be range(1, n + 1)
        result *= i
    return result


def power(base, exp):
    """Compute base raised to the power of exp (non-negative integer exp).

    Expected: power(2, 3) == 8, power(5, 0) == 1
    Bug: uses addition instead of multiplication.
    """
    result = 1
    for _ in range(exp):
        result += base  # BUG: should be result *= base
    return result


def safe_sqrt(n):
    """Compute the square root of n, returning None for negative inputs.

    Expected: safe_sqrt(4) == 2.0, safe_sqrt(0) == 0.0, safe_sqrt(-1) == None
    Bug: missing edge case for negative numbers.
    """
    return math.sqrt(n)  # BUG: no check for negative n
