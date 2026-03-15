#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

cat > "$WORKSPACE/alerts.json" <<'JSON'
[
  {
    "rule_id": "rule-001",
    "rule_name": "High Error Rate",
    "severity": "critical",
    "triggered_at": "2026-03-10T14:10:00",
    "matching_lines": [13, 14, 15, 16, 17, 18, 23, 25, 27, 29],
    "message": "10 ERROR level log entries detected, exceeding threshold of 5. Errors include database connection failures, connection pool exhaustion, and internal server errors."
  },
  {
    "rule_id": "rule-002",
    "rule_name": "Database Connection Failure",
    "severity": "critical",
    "triggered_at": "2026-03-10T14:10:05",
    "matching_lines": [14, 15, 16, 17],
    "message": "Database connection failures detected: initial connection refused on port 5432 followed by 3 failed retry attempts."
  },
  {
    "rule_id": "rule-003",
    "rule_name": "Memory Threshold Exceeded",
    "severity": "high",
    "triggered_at": "2026-03-10T14:14:30",
    "matching_lines": [28, 30],
    "message": "Memory usage exceeded 90% threshold: peaked at 92% and 95% before emergency GC brought it down to 87%."
  }
]
JSON

cat > "$WORKSPACE/incident_report.md" <<'MARKDOWN'
# Incident Report

## Timeline

| Time | Event |
|------|-------|
| 14:00:01 | Application started successfully |
| 14:02:00 | First warning: response time exceeded 500ms |
| 14:10:00 | First error: request timeout after 30s |
| 14:10:05 | Database connection failed (port 5432) |
| 14:10:06-08 | Three database reconnection retries failed |
| 14:10:09 | Service degraded: database unavailable |
| 14:10:10 | System fell back to cached data |
| 14:12:01 | Connection pool exhausted |
| 14:14:30 | Memory usage exceeded 90% (reached 92%) |
| 14:15:01 | Memory usage peaked at 95% |
| 14:15:30 | Emergency GC triggered |
| 14:16:00 | Memory reduced to 87% after GC |
| 14:17:00 | Database connection restored |
| 14:17:01 | Connection pool replenished |
| 14:45:00 | System stable, all services operational |

## Alerts Triggered

### 1. High Error Rate (rule-001) - CRITICAL
10 ERROR-level entries detected within the log period, exceeding the threshold of 5. Errors span from 14:10:00 to 14:15:00.

### 2. Database Connection Failure (rule-002) - CRITICAL
Database connection refused on port 5432 at 14:10:05. Three retry attempts all failed before the system fell back to cached data.

### 3. Memory Threshold Exceeded (rule-003) - HIGH
Memory usage exceeded 90% at 14:14:30 (92%) and peaked at 95% at 14:15:01. Emergency garbage collection was triggered to recover.

## Impact Assessment

- **Duration**: Approximately 7 minutes of degraded service (14:10 - 14:17)
- **Affected Services**: Database-dependent API endpoints (/api/users, /api/orders)
- **User Impact**: 6 failed requests during the incident window
- **Data Integrity**: No data loss detected; cached responses served during outage

## Recommended Actions

1. **Investigate database outage**: Determine root cause of PostgreSQL connection refusal on port 5432
2. **Increase connection pool resilience**: Add circuit breaker pattern for database connections
3. **Tune memory management**: Adjust GC parameters to prevent memory climbing above 90%
4. **Add proactive monitoring**: Set memory warning threshold at 80% for earlier alerts
5. **Review retry strategy**: Consider exponential backoff for database reconnection attempts
MARKDOWN

echo "Solution written to $WORKSPACE/"
