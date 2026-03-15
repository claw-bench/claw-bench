# Task: Debug a Calculator Module

You are given `workspace/calculator.py` which contains three functions with logical bugs. Fix all three bugs.

## Bugs to Fix

1. **`factorial(n)`** -- Has an off-by-one error in the range, producing incorrect results.
2. **`power(base, exp)`** -- Uses the wrong operator internally (addition instead of multiplication).
3. **`safe_sqrt(n)`** -- Missing edge case handling for negative numbers (should return `None` for negative input).

## Requirements

1. Fix all three bugs while preserving the original function signatures.
2. Do not add new functions or change the function names.
3. The fixed functions must pass the test cases described in the docstrings.

## Output

Save the fixed file to `workspace/calculator.py` (overwrite in place).
