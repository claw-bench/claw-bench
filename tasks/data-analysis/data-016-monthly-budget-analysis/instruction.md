# Task: Monthly Budget vs Actual Analysis

You are given two files in the workspace:

- `workspace/budget.csv` -- contains budget targets per spending category with columns: `category`, `budget_amount`.
- `workspace/transactions.csv` -- contains individual transactions with columns: `date`, `category`, `amount`, `description`.

## Requirements

1. Read both CSV files.
2. For each category in the budget, sum all matching transactions to get the actual spending.
3. Compute the difference as `budget_amount - actual` for each category.
4. Classify each category:
   - `"over-budget"` if actual exceeds the budget amount.
   - `"under-budget"` if actual is less than the budget amount.
   - `"on-budget"` if actual equals the budget amount exactly.
5. Produce `workspace/budget_report.json` with the following structure:

```json
{
  "month": "2026-03",
  "summary": [
    {
      "category": "<string>",
      "budget": <number>,
      "actual": <number>,
      "difference": <number>,
      "status": "<over-budget|under-budget|on-budget>"
    }
  ],
  "total_budget": <number>,
  "total_actual": <number>,
  "total_difference": <number>,
  "over_budget_categories": ["<category>", ...],
  "under_budget_categories": ["<category>", ...]
}
```

6. The `summary` list should contain one entry per budget category, in the same order as they appear in `budget.csv`.
7. Round all monetary values to 2 decimal places.
8. `over_budget_categories` and `under_budget_categories` should list category names sorted alphabetically.

## Output

Save the JSON report to `workspace/budget_report.json`.
