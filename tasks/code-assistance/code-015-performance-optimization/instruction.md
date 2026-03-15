# Task: Performance Optimization

You are given `workspace/slow.py` containing three intentionally slow functions. Optimize each function to run **at least 10x faster** while producing the exact same outputs.

## Functions to Optimize

1. **`find_duplicates(items)`** -- Finds duplicate values in a list. Currently uses O(n^2) nested loops.
2. **`count_words(text)`** -- Counts word frequencies in a text. Currently rebuilds the dict inefficiently.
3. **`fibonacci(n)`** -- Computes the nth Fibonacci number. Currently uses naive recursion without memoization.

## Requirements

1. Each function must return the exact same result as the original.
2. Each function must be at least 10x faster on the provided benchmark inputs.
3. Do not add any external library dependencies (stdlib only).
4. Do not change function signatures.

## Output

Save the optimized file to `workspace/slow.py` (overwrite in place).
