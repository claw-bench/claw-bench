#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

python - "$WORKSPACE" << 'PYEOF'
import sys
import json

ws = sys.argv[1]

def describe_schedule(minute, hour, dom, month, dow):
    """Produce a human-readable description of a cron schedule."""
    if minute.startswith("*/"):
        return f"Every {minute[2:]} minutes"
    if month != "*" and dom != "*" and hour != "*":
        # Specific month and day
        months = {
            "1": "January", "2": "February", "3": "March", "4": "April",
            "5": "May", "6": "June", "7": "July", "8": "August",
            "9": "September", "10": "October", "11": "November", "12": "December"
        }
        month_name = months.get(month, month)
        return f"Yearly on {month_name} {int(dom)} at {hour.zfill(2)}:{minute.zfill(2)}"
    if dom != "*" and month == "*":
        return f"Monthly on day {int(dom)} at {hour.zfill(2)}:{minute.zfill(2)}"
    if dow == "0":
        return f"Weekly on Sunday at {hour.zfill(2)}:{minute.zfill(2)}"
    if dow == "1-5":
        return f"Weekdays at {hour.zfill(2)}:{minute.zfill(2)}"
    if "," in hour:
        parts = hour.split(",")
        times = " and ".join(f"{h.zfill(2)}:{minute.zfill(2)}" for h in parts)
        return f"Daily at {times}"
    if hour == "*" and minute == "0":
        return "Every hour at minute 0"
    if hour != "*" and dom == "*" and dow == "*":
        return f"Daily at {hour.zfill(2)}:{minute.zfill(2)}"
    return f"{minute} {hour} {dom} {month} {dow}"

jobs = []
with open(f"{ws}/crontab.txt") as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(None, 5)
        minute, hour, dom, month, dow = parts[0], parts[1], parts[2], parts[3], parts[4]
        command = parts[5]
        cron_expr = f"{minute} {hour} {dom} {month} {dow}"
        schedule_human = describe_schedule(minute, hour, dom, month, dow)
        jobs.append({
            "command": command,
            "schedule_human": schedule_human,
            "cron_expression": cron_expr
        })

result = {
    "jobs": jobs,
    "total_jobs": len(jobs)
}

with open(f"{ws}/cron_schedule.json", "w") as f:
    json.dump(result, f, indent=2)
PYEOF
