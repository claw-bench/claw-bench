#!/usr/bin/env bash
# Oracle solution for data-017-employee-attendance-report
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

python - "$WORKSPACE" << 'PYEOF'
import sys
import csv
import json
from collections import defaultdict

ws = sys.argv[1]

# Read attendance data
records = defaultdict(list)
with open(f'{ws}/attendance.csv', newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        records[row['employee']].append(row)

employees = []
all_dates = set()

for name in sorted(records.keys()):
    rows = records[name]
    total_hours = 0.0
    late_dates = []

    for row in rows:
        all_dates.add(row['date'])
        # Parse times
        ci_h, ci_m = map(int, row['clock_in'].split(':'))
        co_h, co_m = map(int, row['clock_out'].split(':'))
        hours = (co_h * 60 + co_m - ci_h * 60 - ci_m) / 60.0
        total_hours += hours

        # Check lateness (strictly after 09:00)
        clock_in_minutes = ci_h * 60 + ci_m
        if clock_in_minutes > 9 * 60:
            late_dates.append(row['date'])

    num_days = len(rows)
    total_hours = round(total_hours, 2)
    avg_hours = round(total_hours / num_days, 2)
    late_days = len(late_dates)
    punctuality_rate = round((num_days - late_days) / num_days, 2)

    employees.append({
        'name': name,
        'total_hours': total_hours,
        'avg_hours_per_day': avg_hours,
        'late_days': late_days,
        'late_dates': sorted(late_dates),
        'punctuality_rate': punctuality_rate
    })

# Team statistics
team_avg_hours = round(sum(e['total_hours'] for e in employees) / len(employees), 2)
total_late = sum(e['late_days'] for e in employees)

# Most punctual: highest punctuality_rate, tie-break by most total_hours
most_punctual = max(employees, key=lambda e: (e['punctuality_rate'], e['total_hours']))

sorted_dates = sorted(all_dates)
period = f"{sorted_dates[0]} to {sorted_dates[-1]}"

result = {
    'period': period,
    'employees': employees,
    'team_avg_hours': team_avg_hours,
    'most_punctual': most_punctual['name'],
    'total_late_arrivals': total_late
}

with open(f'{ws}/attendance_report.json', 'w') as f:
    json.dump(result, f, indent=2)
PYEOF

echo "Attendance report written to $WORKSPACE/attendance_report.json"
