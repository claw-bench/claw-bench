# Task: Pairwise Correlation Analysis

You are given a CSV file at `workspace/dataset.csv` with 5 numeric columns: `height`, `weight`, `age`, `income`, `score`.

## Requirements

1. Read `workspace/dataset.csv`.
2. Compute the Pearson correlation coefficient for every pair of numeric columns.
3. Write the full correlation matrix to `workspace/correlations.csv`:
   - First column should be named `variable`
   - Remaining columns should be the variable names
   - Values rounded to 4 decimal places
4. Identify the top 3 most strongly correlated pairs (by absolute value, excluding self-correlations).
5. Write to `workspace/top_correlations.json` as a list of objects with keys: `var1`, `var2`, `correlation` (rounded to 4 decimal places), sorted by absolute correlation descending.

## Output

Save `workspace/correlations.csv` and `workspace/top_correlations.json`.
