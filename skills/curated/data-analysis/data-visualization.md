# Data Visualization Guidance

## Chart Selection
- Bar chart: comparing categories
- Line chart: trends over time
- Scatter plot: correlations between variables
- Pie chart: parts of a whole (use sparingly)

## Statistical Summary
- Always report: count, mean, median, std dev, min, max
- For grouped data: group-wise statistics with totals
- Use percentiles (25th, 75th) for distribution understanding

## Outlier Detection
- IQR method: Q1 - 1.5*IQR to Q3 + 1.5*IQR
- Z-score method: values beyond ±3 standard deviations
- Report outliers separately with context

## Aggregation Patterns
- GROUP BY equivalent: use `defaultdict(list)` then aggregate
- Multi-level grouping: nested dictionaries
- Time-based: resample to consistent intervals before aggregating
