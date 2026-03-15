# Task: Performance Diagnostic

You are given three CSV files in `workspace/metrics/` containing 24 hours of system performance data sampled every hour:
- `cpu.csv` - CPU usage percentages
- `memory.csv` - Memory usage percentages
- `disk_io.csv` - Disk I/O in MB/s

## Requirements

1. Read all three metric files.
2. Analyze the data to identify:
   - **Anomalies**: Data points that significantly deviate from the norm (> 2 standard deviations from the mean, or sudden spikes/drops)
   - **Bottlenecks**: Resources consistently at high utilization (> 80% for CPU/memory, > 100 MB/s for disk I/O)
   - **Time windows**: When issues occurred
3. Generate a JSON report:

```json
{
  "analysis_period": {
    "start": "2024-03-15T00:00:00",
    "end": "2024-03-15T23:00:00",
    "data_points": 24
  },
  "cpu": {
    "mean": <float>,
    "max": <float>,
    "min": <float>,
    "anomalies": [
      {"hour": <int>, "value": <float>, "type": "spike|drop"}
    ]
  },
  "memory": {
    "mean": <float>,
    "max": <float>,
    "min": <float>,
    "anomalies": [
      {"hour": <int>, "value": <float>, "type": "spike|drop"}
    ]
  },
  "disk_io": {
    "mean": <float>,
    "max": <float>,
    "min": <float>,
    "anomalies": [
      {"hour": <int>, "value": <float>, "type": "spike|drop"}
    ]
  },
  "bottlenecks": [
    {
      "resource": "cpu|memory|disk_io",
      "severity": "warning|critical",
      "time_window": {"start_hour": <int>, "end_hour": <int>},
      "description": "<description>"
    }
  ],
  "recommendations": [
    "<actionable recommendation>"
  ]
}
```

## Output

Save the report to `workspace/diagnosis.json`.
