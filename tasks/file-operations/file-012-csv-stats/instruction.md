# Task: CSV Column Extraction and Statistics

You are given a CSV file at `workspace/sales.csv`. Extract the "price" column and compute summary statistics.

## Requirements

1. Read `workspace/sales.csv`.
2. Extract all values from the `price` column.
3. Compute the following statistics:
   - `min`: minimum price
   - `max`: maximum price
   - `mean`: arithmetic mean (average) price
   - `median`: median price
4. Write the results to `workspace/stats.json` as a JSON object.
5. All values should be numbers (not strings), rounded to 2 decimal places.

## Expected Output Format

```json
{
    "min": 9.99,
    "max": 99.99,
    "mean": 45.50,
    "median": 42.00
}
```

## Output

Save the statistics to `workspace/stats.json`.
