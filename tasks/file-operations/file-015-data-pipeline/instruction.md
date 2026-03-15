# Task: Complex Data Transformation Pipeline

You are given a messy CSV file at `workspace/raw_data.csv`. Clean, normalize, and transform it.

## Requirements

### Step 1: Clean the data
1. Read `workspace/raw_data.csv`.
2. Remove any rows that have empty/null values in **any** column (cells that are empty strings or contain only whitespace).
3. Normalize the `name` column to Title Case (e.g., "JOHN DOE" -> "John Doe", "jane smith" -> "Jane Smith").
4. Normalize the `city` column to Title Case.
5. Normalize the `date` column to `YYYY-MM-DD` format. Input dates may be in formats like:
   - `MM/DD/YYYY` (e.g., 01/15/2025)
   - `DD-MM-YYYY` (e.g., 15-01-2025)
   - `YYYY/MM/DD` (e.g., 2025/01/15)
   - `Month DD, YYYY` (e.g., January 15, 2025)

### Step 2: Enrich the data
6. Add a computed column `total` which equals `quantity * price` (rounded to 2 decimal places).

### Step 3: Output
7. Write the cleaned data to `workspace/clean_data.csv` with columns: `name,city,date,product,quantity,price,total`
8. Write a summary to `workspace/summary.json` with:
   - `total_rows`: number of rows in the cleaned data
   - `total_revenue`: sum of all `total` values (rounded to 2 decimal places)
   - `average_order`: mean of all `total` values (rounded to 2 decimal places)
   - `cities`: sorted list of unique cities in the cleaned data

## Output

Save the cleaned CSV to `workspace/clean_data.csv` and the summary to `workspace/summary.json`.
