# System Analysis Skill

## Overview
This skill provides guidance on system administration tasks including log parsing,
process and port analysis, cron expression syntax, and configuration auditing.

## Log Parsing

### Syslog Format
Standard syslog lines follow this structure:
`<timestamp> <hostname> <process>[<pid>]: <message>`

```python
import re

SYSLOG_PATTERN = re.compile(
    r"^(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+"  # timestamp
    r"(\S+)\s+"                                       # hostname
    r"(\S+?)(?:\[(\d+)\])?:\s+"                       # process[pid]
    r"(.+)$"                                           # message
)

def parse_syslog(line):
    match = SYSLOG_PATTERN.match(line)
    if match:
        return {
            "timestamp": match.group(1),
            "hostname": match.group(2),
            "process": match.group(3),
            "pid": match.group(4),
            "message": match.group(5),
        }
    return None
```

### Apache/Nginx Access Log (Combined Format)
Format: `<ip> <ident> <user> [<time>] "<request>" <status> <size> "<referer>" "<agent>"`

```python
ACCESS_LOG_PATTERN = re.compile(
    r'(\S+)\s+(\S+)\s+(\S+)\s+'
    r'\[([^\]]+)\]\s+'
    r'"([^"]+)"\s+'
    r'(\d{3})\s+(\d+|-)\s+'
    r'"([^"]*)"\s+"([^"]*)"'
)

def parse_access_log(line):
    match = ACCESS_LOG_PATTERN.match(line)
    if match:
        return {
            "ip": match.group(1),
            "time": match.group(4),
            "request": match.group(5),
            "status": int(match.group(6)),
            "size": match.group(7),
            "referer": match.group(8),
            "user_agent": match.group(9),
        }
    return None
```

### Log Analysis Patterns
- **Error extraction**: Filter lines by severity keywords (ERROR, WARN, CRITICAL).
- **Frequency counting**: Count occurrences per source, per hour, or per status code.
- **Anomaly detection**: Flag lines where numeric fields exceed historical thresholds.
- **Time-window aggregation**: Group log entries into buckets for trend analysis.

```python
from collections import Counter

def count_status_codes(log_entries):
    codes = Counter(entry["status"] for entry in log_entries)
    return codes.most_common()

def filter_errors(log_entries):
    return [e for e in log_entries if e["status"] >= 400]
```

## Process and Port Analysis

### Identifying Running Processes
```bash
# List all processes with full detail
ps aux

# Find processes by name
ps aux | grep <process_name>

# Show process tree
pstree -p <pid>
```

### Port Analysis
```bash
# List listening ports (Linux)
ss -tlnp
netstat -tlnp

# List listening ports (macOS)
lsof -iTCP -sTCP:LISTEN -nP

# Check what process uses a specific port
lsof -i :<port_number>
```

### Resource Monitoring
- **CPU**: Check `%CPU` column in `top` or `ps aux --sort=-%cpu`.
- **Memory**: Look at `RSS` (resident set size) for actual memory usage.
- **Disk I/O**: Use `iotop` or `iostat` for per-process I/O stats.
- **Open files**: `lsof -p <pid>` shows all file descriptors for a process.

## Cron Expression Syntax

### Five-Field Format
```
* * * * *
| | | | |
| | | | +-- Day of week (0-7, 0 and 7 are Sunday)
| | | +---- Month (1-12)
| | +------ Day of month (1-31)
| +-------- Hour (0-23)
+---------- Minute (0-59)
```

### Special Characters
- `*`: Every value in the field.
- `,`: List separator (e.g., `1,15` means the 1st and 15th).
- `-`: Range (e.g., `9-17` means 9 through 17 inclusive).
- `/`: Step (e.g., `*/5` in minute field means every 5 minutes).

### Common Examples
```
0 * * * *       # Every hour at minute 0
30 9 * * 1-5    # Weekdays at 9:30 AM
0 0 1 * *       # First day of each month at midnight
*/10 * * * *    # Every 10 minutes
0 6,18 * * *    # At 6 AM and 6 PM daily
```

### Validation Approach
1. Split the expression into exactly 5 (or 6 with seconds) fields.
2. Validate each field against its allowed range.
3. Expand special characters to verify they produce valid values.
4. Check for logical conflicts (e.g., day 31 in a month-restricted schedule).

## Configuration File Auditing

### General Checklist
- **Syntax validation**: Parse the config file with the appropriate parser
  (INI, YAML, TOML, JSON) and check for syntax errors.
- **Default overrides**: Identify values that differ from known defaults.
- **Security settings**: Check file permissions, credential exposure, and
  TLS/SSL configuration.
- **Consistency**: Cross-reference related settings for contradictions.

### Common Config Formats
```python
# INI files
import configparser
config = configparser.ConfigParser()
config.read("app.conf")

# YAML files
import yaml
with open("config.yaml") as f:
    config = yaml.safe_load(f)

# TOML files
import tomllib  # Python 3.11+
with open("config.toml", "rb") as f:
    config = tomllib.load(f)
```

### Permission Auditing
```bash
# Check file permissions (should not be world-readable for sensitive files)
stat -c '%a %U %G %n' /etc/myapp/config.conf

# Find world-writable files in a directory
find /etc/myapp -perm -o+w -type f

# Check ownership
ls -la /etc/myapp/
```

### Key Audit Points
- Credentials should not appear in plaintext; check for environment variable
  references or vault integrations.
- Listen addresses: services should bind to specific interfaces, not 0.0.0.0,
  unless intentional.
- Logging level: production systems should not run at DEBUG level.
- Timeouts and limits: verify connection timeouts, max request sizes, and
  rate limits are set to reasonable values.

## Best Practices
- Always back up configuration files before modifying them.
- Use structured parsing libraries instead of regex for config files.
- When analyzing logs, process line by line for memory efficiency on large files.
- Correlate timestamps across multiple log sources using a common time reference.
