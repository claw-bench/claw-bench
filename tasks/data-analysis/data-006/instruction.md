# Task: Time Series Aggregation

You are given a CSV file at `workspace/daily_sales.csv` with columns: `date`, `amount`.

## Requirements

1. Read `workspace/daily_sales.csv`.
2. Aggregate by **ISO week**: group by ISO year and ISO week number, sum amounts.
   - Write to `workspace/weekly.csv` with columns: `week` (format `YYYY-WNN`, e.g., `2025-W01`), `total_amount`
   - Sort chronologically.
3. Aggregate by **month**: group by year-month, sum amounts.
   - Write to `workspace/monthly.csv` with columns: `month` (format `YYYY-MM`), `total_amount`
   - Sort chronologically.
4. Round all amounts to 2 decimal places.

## Output

Save `workspace/weekly.csv` and `workspace/monthly.csv`.
