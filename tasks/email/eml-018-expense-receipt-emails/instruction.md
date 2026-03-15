# Task: Extract Expenses from Receipt Emails

Parse receipt confirmation emails to extract vendor names, amounts, dates, and categories, then compile a structured expense report.

## Input

- `workspace/receipts/` — a directory containing 6 receipt confirmation email JSON files

Each email has this structure:
```json
{
  "from": "noreply@vendor.com",
  "to": "you@company.com",
  "subject": "Your receipt",
  "date": "2026-03-XX",
  "body": "Natural language receipt details..."
}
```

## Requirements

1. Read all JSON email files from `workspace/receipts/`
2. Parse each email body to extract:
   - **Vendor name** (e.g., "Amazon", "Starbucks", "Uber", "AWS", "Office Depot", "Zoom")
   - **Amount** as a numeric value (e.g., 45.99)
   - **Date** from the email's date field
   - **Category** — infer from the vendor/context:
     - `office-supplies` for Amazon and Office Depot purchases
     - `meals` for Starbucks / food purchases
     - `transportation` for Uber / ride-share
     - `cloud-services` for AWS billing
     - `software` for Zoom / software subscriptions
3. Calculate the total of all expenses
4. Calculate subtotals grouped by category

## Output

Write the expense report to `workspace/expense_report.json` with the following structure:

```json
{
  "expenses": [
    {
      "vendor": "Amazon",
      "amount": 45.99,
      "date": "2026-03-08",
      "category": "office-supplies"
    }
  ],
  "total": 342.53,
  "by_category": {
    "office-supplies": 135.29,
    "meals": 12.50,
    "transportation": 23.75,
    "cloud-services": 156.00,
    "software": 14.99
  }
}
```

Field specifications:
- `expenses` — array of expense objects, one per receipt email
- Each expense has: `vendor` (string), `amount` (number, not string), `date` (string YYYY-MM-DD), `category` (string)
- `total` — number, sum of all expense amounts
- `by_category` — object mapping category names to their subtotals (numbers)
- All monetary amounts must be numeric values, not strings
