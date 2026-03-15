# Task: Log to Alert

Analyze application logs and alert rules to identify incidents and produce alerts and an incident report.

## Input Files

- `workspace/application.log` - Application log file with timestamped entries
- `workspace/alert_rules.json` - Alert rules defining patterns and severity

## Objective

1. Parse `workspace/application.log`.
2. Evaluate each alert rule from `workspace/alert_rules.json` against the log.
3. Generate `workspace/alerts.json` with triggered alerts.
4. Generate `workspace/incident_report.md` with a timeline and analysis.

## Output: alerts.json

```json
[
  {
    "rule_id": "rule-001",
    "rule_name": "Name from rules",
    "severity": "critical",
    "triggered_at": "2026-03-10T14:32:00",
    "matching_lines": [14, 15, 16],
    "message": "Description of what triggered this alert"
  }
]
```

## Output: incident_report.md

Must include:
- **Timeline**: Chronological list of significant events from the log
- **Alerts Triggered**: Summary of each triggered alert
- **Impact Assessment**: Brief description of potential impact
- **Recommended Actions**: Steps to resolve
