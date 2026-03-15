# Task: Outlier Detection Using IQR

You are given a CSV file at `workspace/measurements.csv` with columns: `id`, `value`.

## Requirements

1. Read `workspace/measurements.csv`.
2. Use the IQR (Interquartile Range) method to detect outliers:
   - Compute Q1 (25th percentile) and Q3 (75th percentile)
   - IQR = Q3 - Q1
   - Lower bound = Q1 - 1.5 * IQR
   - Upper bound = Q3 + 1.5 * IQR
   - Any value outside [lower_bound, upper_bound] is an outlier
3. Use the **exclusive** (interpolation) method for quartile computation. Specifically, use numpy-style `percentile` with linear interpolation, or the standard `statistics.quantiles(data, n=4)` approach which splits at n=4 boundaries.
4. Write outlier rows (with `id` and `value` columns) to `workspace/outliers.csv`.
5. Write analysis stats to `workspace/analysis.json` with keys: `q1`, `q3`, `iqr`, `lower_bound`, `upper_bound`, `outlier_count`. All values rounded to 2 decimal places.

## Output

Save `workspace/outliers.csv` and `workspace/analysis.json`.
