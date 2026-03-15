# Task: Log File Filtering

You are given a log file at `workspace/app.log`. Filter out only the ERROR and WARN entries.

## Requirements

1. Read `workspace/app.log`.
2. Extract only lines that contain the log level `ERROR` or `WARN`.
3. Preserve the original line format and order.
4. Write the filtered lines to `workspace/errors.txt`.
5. Each filtered line should be kept exactly as it appears in the original log.

## Log Format

Each log line follows this format:

```
YYYY-MM-DD HH:MM:SS [LEVEL] message
```

Where LEVEL is one of: INFO, DEBUG, WARN, ERROR.

## Output

Save the filtered log lines to `workspace/errors.txt`.
