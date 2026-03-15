# Task: Data Cleaning Pipeline

You are given a CSV file at `workspace/dirty_data.csv` with columns: `id`, `name`, `email`, `phone`, `date_joined`, `salary`.

## Requirements

1. Read `workspace/dirty_data.csv`.
2. Clean the data:
   - **Remove duplicate rows** (by `id`; keep the first occurrence).
   - **Handle missing values**: drop rows where `id` or `name` is missing. For `salary`, fill missing values with the median salary of non-missing rows.
   - **Normalize email**: convert to lowercase, trim whitespace.
   - **Normalize phone**: remove all non-digit characters, ensure 10-digit format (no country code).
   - **Normalize date_joined**: convert all dates to `YYYY-MM-DD` format (input may be `MM/DD/YYYY`, `DD-MM-YYYY`, or `YYYY-MM-DD`).
3. Write cleaned data to `workspace/clean_data.csv` (same columns, sorted by `id`).
4. Write `workspace/cleaning_report.json` with:
   - `duplicates_removed`: count of duplicate rows removed
   - `missing_values_filled`: count of missing salary values filled
   - `rows_dropped`: count of rows dropped due to missing id/name
   - `total_clean_rows`: final row count

## Output

Save `workspace/clean_data.csv` and `workspace/cleaning_report.json`.
