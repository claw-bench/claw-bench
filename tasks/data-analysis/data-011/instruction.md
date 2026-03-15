# Task: Comprehensive Analysis Report

You are given a CSV file at `workspace/company_data.csv` with columns: `company`, `region`, `quarter`, `revenue`, `employees`, `satisfaction_score`.

## Requirements

1. Read `workspace/company_data.csv`.
2. Generate `workspace/report.md` containing:
   - **Summary Statistics** section: total revenue, average revenue, total employees, average satisfaction score (all rounded to 2 decimal places)
   - **Top Performers** section: top 5 companies by total revenue
   - **Regional Trends** section: average revenue by region
   - **Quarterly Trends** section: total revenue per quarter
   - **Recommendations** section: at least 2 actionable recommendations based on the data
3. Generate `workspace/charts_data.json` with data for at least 3 chart types:
   - `bar_chart`: data for revenue by region (keys: `labels`, `values`)
   - `line_chart`: data for quarterly revenue trend (keys: `labels`, `values`)
   - `pie_chart`: data for employee distribution by region (keys: `labels`, `values`)

## Output

Save `workspace/report.md` and `workspace/charts_data.json`.
