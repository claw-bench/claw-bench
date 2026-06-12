# Longest Increasing Subsequence (LIS)

Given an array of integers, find the **longest strictly increasing subsequence**.

A subsequence is derived from the array by deleting zero or more elements without
changing the order of the remaining elements. "Strictly increasing" means each
element is strictly greater than the previous one (no equal elements).

## Task

1. Read the input array from `input.json` (key: `array`).
2. Compute the length of the LIS.
3. Recover one valid longest increasing subsequence.
4. Write the result to `solution.json` with keys `length` and `subsequence`.

## Constraints

- Use an efficient algorithm: O(n²) dynamic programming or O(n log n) patience sorting.
- Do not brute-force enumerate all subsequences.
- Any valid subsequence of maximum length is acceptable.
