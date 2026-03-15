# Task: Outlier Detection Report

You are given a dataset at `workspace/measurements.csv` containing sensor readings with the columns: `sensor_id`, `timestamp`, `value`, `unit`.

## Requirements

1. Read `workspace/measurements.csv`.
2. For each sensor, compute the first quartile (Q1), third quartile (Q3), and the interquartile range (IQR = Q3 - Q1).
3. Identify outliers as any record whose `value` is below `Q1 - 1.5 * IQR` or above `Q3 + 1.5 * IQR` (computed per sensor).
4. For each outlier, compute its z-score relative to that sensor's mean and standard deviation. Round the z-score to 2 decimal places.
5. Produce `workspace/outlier_report.json` with the following structure:

```json
{
  "total_records": <int>,
  "outlier_count": <int>,
  "outliers": [
    {
      "sensor_id": "<string>",
      "timestamp": "<string>",
      "value": <number>,
      "z_score": <number>
    }
  ],
  "summary_by_sensor": {
    "<sensor_id>": {
      "total_readings": <int>,
      "outlier_count": <int>,
      "mean": <number>,
      "std": <number>,
      "q1": <number>,
      "q3": <number>
    }
  }
}
```

6. The `outliers` list should be sorted by absolute z-score in descending order.
7. Round all floating-point values in the output to 2 decimal places.

## Output

Save the JSON report to `workspace/outlier_report.json`.
