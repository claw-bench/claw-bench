# Task: Write Unit Tests for Calculator

You are given a Python module `calculator.py` in the workspace directory. It contains a `Calculator` class with four methods:

- `add(a, b)` - returns the sum of a and b
- `subtract(a, b)` - returns the difference of a and b
- `multiply(a, b)` - returns the product of a and b
- `divide(a, b)` - returns the quotient of a and b; raises `ValueError` on division by zero

## Requirements

Write a pytest test file at `workspace/test_calculator.py` that:

1. Tests each of the four operations with at least two different inputs each.
2. Tests that `divide(x, 0)` raises a `ValueError`.
3. Tests edge cases such as negative numbers and zero.
4. All tests must pass when run with `pytest workspace/test_calculator.py`.

## Output

Save the test file to `workspace/test_calculator.py`.
