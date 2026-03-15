# Task: Create Pivot Table from Transactions

You are given a CSV file at `workspace/transactions.csv` with columns: `date`, `category`, `amount`.

## Requirements

1. Read `workspace/transactions.csv`.
2. Create a pivot table where:
   - Rows are months (format: `YYYY-MM`)
   - Columns are categories
   - Values are the sum of `amount` for each month-category pair
3. Sort rows by month chronologically.
4. Add a `Total` row at the bottom summing all months per category.
5. Write the result to `workspace/pivot.csv`.

The first column should be named `month`.

## Output

Save the pivot table to `workspace/pivot.csv`.
