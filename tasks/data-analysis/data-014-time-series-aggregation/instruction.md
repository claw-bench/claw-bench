# Task: Time Series Aggregation

You are given hourly metrics data at `workspace/metrics.csv` with columns: `timestamp`, `cpu_percent`, `memory_mb`, `requests_per_sec`.

## Requirements

1. Read `workspace/metrics.csv`.
2. Aggregate the data into daily summaries. Each day should produce:
   - `date`: the date string in `YYYY-MM-DD` format
   - `avg_cpu`: average CPU percentage for that day, rounded to 2 decimal places
   - `max_cpu`: maximum CPU percentage for that day
   - `avg_memory`: average memory in MB for that day, rounded to 2 decimal places
   - `total_requests`: sum of requests_per_sec values for that day (treating each hourly reading as the count for that hour)
3. Determine a `trend` for each metric across the daily aggregates:
   - Compare the first day's value to the last day's value for each metric.
   - For `avg_cpu`: if the last day's avg_cpu is more than 5% higher than the first day's, it is "increasing"; if more than 5% lower, "decreasing"; otherwise "stable".
   - For `avg_memory`: same logic with a 5% threshold.
   - For `total_requests`: same logic with a 5% threshold.
4. Produce `workspace/aggregated.json` with the following structure:

```json
{
  "daily": [
    {
      "date": "YYYY-MM-DD",
      "avg_cpu": <number>,
      "max_cpu": <number>,
      "avg_memory": <number>,
      "total_requests": <number>
    }
  ],
  "trend": {
    "cpu": "increasing|decreasing|stable",
    "memory": "increasing|decreasing|stable",
    "requests": "increasing|decreasing|stable"
  }
}
```

5. The `daily` list should be sorted by date in ascending order.

## Output

Save the JSON report to `workspace/aggregated.json`.
