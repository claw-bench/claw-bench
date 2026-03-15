# Task: Analyze Access Logs for Security Incidents

Analyze `workspace/access.log` to detect suspicious activity patterns.

## Requirements

1. Read `workspace/access.log` (Apache-style combined log format, 100 lines).
2. Detect the following incident patterns:
   - **Brute force attack**: Multiple failed login attempts (HTTP 401) from the same IP in a short window
   - **Suspicious scanning**: Single IP requesting many different paths rapidly (especially admin/sensitive paths)
   - **Off-hours access**: Successful access to admin endpoints between 00:00-05:00
3. Write `workspace/security_incidents.json` as a JSON array of objects, each with:
   - `type`: one of `"brute_force"`, `"scanning"`, `"off_hours_access"`
   - `source_ip`: the IP address involved
   - `time_window`: start and end timestamps of the activity
   - `description`: summary of the suspicious activity
   - `evidence`: array of relevant log line numbers
   - `severity`: `"high"`, `"medium"`, or `"low"`

## Notes

- There are 3 distinct incident patterns to detect.
- Normal traffic is mixed in; do not flag legitimate requests.
- Timestamps are in the format `[DD/Mon/YYYY:HH:MM:SS +0000]`.

## Output

Save results to `workspace/security_incidents.json`.
