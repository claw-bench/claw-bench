# Log Analysis with Config

You have two files in your workspace:
- `server.log` — a server log file with timestamped entries
- `config.yaml` — a configuration file defining service thresholds and expected settings

**Task:** Cross-reference the log file with the configuration to produce a file called `report.txt` in the workspace.

## Requirements

The output `report.txt` must contain the following sections in order:

### 1. Summary
A line: `Total log entries: <N>` where N is the total number of log lines.
A line: `Error count: <N>` where N is the number of lines with level ERROR.
A line: `Warning count: <N>` where N is the number of lines with level WARNING.

### 2. Threshold Violations
A section starting with the line `Threshold Violations:` followed by one line per violation.
For each service defined in config.yaml under `services`, count the number of ERROR log entries whose message contains that service name (case-insensitive). If the count exceeds the service's `max_errors` threshold, output:
`- <service_name>: <actual_count> errors (threshold: <max_errors>)`
List violations in alphabetical order by service name.

### 3. Unknown Services
A section starting with the line `Unknown Services:` followed by one line per unknown service.
For each unique service name found in log messages (the word immediately after "Service" or "service" in the log message) that is NOT listed in config.yaml, output:
`- <service_name>`
List in alphabetical order.

### 4. Port Mismatch
A section starting with the line `Port Mismatches:` followed by one line per mismatch.
Log entries that mention a port (e.g., `port 9090`) for a known service — if the port differs from the service's configured `port` in config.yaml, output:
`- <service_name>: log port <log_port>, config port <config_port>`
List in alphabetical order by service name. Report each service at most once (use the first occurrence).
