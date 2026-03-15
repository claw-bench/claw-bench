# Task: Markdown Report from Multiple Sources

You are given three files in `workspace/`:

- `sales.csv` - Monthly sales data by salesperson
- `targets.json` - Annual sales targets per salesperson
- `template.md` - A Markdown report template with placeholders

## Requirements

1. Read all three input files.
2. Compute the following metrics:
   - **YTD Total**: Sum of all sales amounts across all salespeople and all months.
   - **Per-person YTD Total**: Sum of each salesperson's sales across all months.
   - **% to Target**: For each salesperson, `(their YTD total / their annual target) * 100`, rounded to 1 decimal place.
   - **Top Performer**: The salesperson with the highest YTD total.
   - **Average Monthly Sale**: YTD Total divided by the number of months in the data, rounded to 2 decimal places.
3. Fill in the template placeholders:
   - `{{YTD_TOTAL}}` - The overall YTD total formatted with commas (e.g., `1,234,567`)
   - `{{AVG_MONTHLY}}` - Average monthly sale formatted with commas and 2 decimal places (e.g., `102,880.58`)
   - `{{TOP_PERFORMER}}` - Name of the top performer
   - `{{TOP_PERFORMER_TOTAL}}` - Top performer's YTD total formatted with commas
   - `{{SALES_TABLE}}` - A Markdown table with columns: Salesperson, YTD Total, Target, % to Target
   - `{{REPORT_DATE}}` - Today's date in YYYY-MM-DD format
4. In the sales table, format dollar amounts with commas (no dollar sign needed). Sort rows by YTD Total descending.
5. Write the result to `workspace/report.md`.

## Output

Save the completed report to `workspace/report.md`.
