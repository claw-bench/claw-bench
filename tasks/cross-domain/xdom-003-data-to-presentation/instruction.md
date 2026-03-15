# Task: Data to Presentation

You have quarterly business data in `workspace/quarterly_data.csv`. Generate a markdown slide presentation and chart data.

## Objective

1. Read and analyze `workspace/quarterly_data.csv`.
2. Compute key metrics per quarter (total revenue, total units sold, average deal size).
3. Generate `workspace/presentation.md` as a markdown slide deck.
4. Generate `workspace/charts_data.json` with structured data for charts.

## Input Format

The CSV has columns: `quarter`, `region`, `product`, `units_sold`, `revenue`, `cost`.

## Output: presentation.md

Use `---` as slide separators. Must include:
- Title slide
- One slide per quarter (Q1 through Q4) with key metrics
- A summary/trends slide comparing all quarters
- Each slide should have the quarter name as heading and bullet points for metrics

## Output: charts_data.json

```json
{
  "quarterly_revenue": {
    "labels": ["Q1", "Q2", "Q3", "Q4"],
    "values": [number, number, number, number]
  },
  "quarterly_units": {
    "labels": ["Q1", "Q2", "Q3", "Q4"],
    "values": [number, number, number, number]
  },
  "regional_revenue": {
    "labels": ["Region1", "Region2", ...],
    "values": [number, number, ...]
  }
}
```

All numeric values must be computed from the CSV data.
