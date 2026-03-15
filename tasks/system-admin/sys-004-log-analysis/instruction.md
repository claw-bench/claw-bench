# Task: Log Analysis

You are given a file at `workspace/syslog.txt` containing 100 lines of simulated syslog entries with timestamps, severities, and source identifiers.

## Requirements

1. Read `workspace/syslog.txt`.
2. Parse each log entry. The format is:
   ```
   YYYY-MM-DD HH:MM:SS SEVERITY source: message text
   ```
   Severities are: INFO, WARNING, ERROR, CRITICAL
3. Generate a JSON report with the following structure:

```json
{
  "total_entries": <count>,
  "severity_counts": {
    "INFO": <count>,
    "WARNING": <count>,
    "ERROR": <count>,
    "CRITICAL": <count>
  },
  "top_error_sources": [
    {"source": "<name>", "error_count": <count>},
    ...
  ],
  "peak_hour": <hour as integer 0-23>,
  "entries_per_hour": {
    "<hour>": <count>,
    ...
  },
  "critical_entries": [
    {"timestamp": "<ts>", "source": "<name>", "message": "<msg>"},
    ...
  ]
}
```

4. `top_error_sources` lists sources with ERROR or CRITICAL entries, sorted by count descending (top 5 max).
5. `peak_hour` is the hour (0-23) with the most log entries.
6. `critical_entries` lists all CRITICAL severity entries.

## Output

Save the report to `workspace/log_analysis.json`.
