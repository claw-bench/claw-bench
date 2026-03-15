# Task: CSV Data Pipeline with Notifications

Process data through a configurable pipeline and generate processing notifications.

## Input Files

- `workspace/input.csv` - 30 rows of order data
- `workspace/pipeline_config.json` - Pipeline configuration with processing steps

## Objective

1. Read `workspace/input.csv` and `workspace/pipeline_config.json`.
2. Apply the pipeline steps in order: filter, transform, aggregate.
3. Write `workspace/output.csv` with filtered and transformed rows.
4. Write `workspace/aggregation.json` with aggregation results.
5. Write `workspace/notification.json` with a summary of what was processed.

## Pipeline Steps

The config defines:
- **filter**: Keep only rows matching the filter criteria (e.g., status == "completed")
- **transform**: Apply transformations (e.g., compute a new column `total` = `quantity * price`)
- **aggregate**: Compute aggregations (e.g., sum of totals by category)

## Output: notification.json

```json
{
  "pipeline_name": "Name from config",
  "input_rows": 30,
  "filtered_rows": 0,
  "output_rows": 0,
  "aggregation_groups": 0,
  "status": "success",
  "summary": "Processed X rows, filtered to Y, aggregated into Z groups"
}
```

All counts must be accurate based on actual processing.
