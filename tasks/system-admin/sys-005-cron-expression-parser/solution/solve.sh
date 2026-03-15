#!/usr/bin/env bash
# Oracle solution for sys-005-cron-expression-parser
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

python3 -c "
import json
from datetime import datetime, timedelta

def describe_cron(minute, hour, dom, month, dow):
    parts = []
    if minute == '*/15':
        return 'Every 15 minutes'
    if minute == '*/5':
        return 'Every 5 minutes'
    if minute == '*' and hour == '*' and dom == '*' and month == '*' and dow == '*':
        return 'Every minute'

    time_desc = ''
    if minute.startswith('*/'):
        time_desc = f'Every {minute[2:]} minutes'
    elif hour.startswith('*/'):
        m = minute if minute != '0' else '00'
        time_desc = f'At minute {m} every {hour[2:]} hours'
    elif ',' in hour:
        hours = hour.split(',')
        times = []
        for h in hours:
            t = f'{int(h):d}:{int(minute):02d}'
            ampm = 'AM' if int(h) < 12 else 'PM'
            h12 = int(h) % 12 or 12
            times.append(f'{h12}:{int(minute):02d} {ampm}')
        time_desc = 'At ' + ', '.join(times)
    else:
        h = int(hour) if hour != '*' else None
        m = int(minute) if minute != '*' else 0
        if h is not None:
            ampm = 'AM' if h < 12 else ('PM' if h < 24 else 'AM')
            h12 = h % 12 or 12
            time_desc = f'At {h12}:{m:02d} {ampm}'

    day_desc = ''
    if dom == '1' and month == '*':
        day_desc = 'on the 1st of every month'
    elif dom != '*':
        if month != '*':
            month_names = {
                '1': 'January', '2': 'February', '3': 'March', '4': 'April',
                '5': 'May', '6': 'June', '7': 'July', '8': 'August',
                '9': 'September', '10': 'October', '11': 'November', '12': 'December'
            }
            months = [month_names[m.strip()] for m in month.split(',')]
            day_desc = f'on the {dom}th of ' + ' and '.join(months)
        else:
            day_desc = f'on day {dom} of every month'
    elif dow == '0' or dow == '7':
        day_desc = 'every Sunday'
    elif dow == '1-5':
        day_desc = 'Monday through Friday'
    elif dow != '*':
        day_names = {'0': 'Sunday', '1': 'Monday', '2': 'Tuesday', '3': 'Wednesday',
                     '4': 'Thursday', '5': 'Friday', '6': 'Saturday', '7': 'Sunday'}
        day_desc = f'on {day_names.get(dow, dow)}'
    else:
        if dom == '*' and month == '*':
            day_desc = 'every day'

    return f'{time_desc} {day_desc}'.strip()

def next_runs_for(minute, hour, dom, month, dow, start, count=3):
    runs = []
    dt = start
    for _ in range(1051920):  # max ~2 years of minutes
        m, h, d, mo, wd = dt.minute, dt.hour, dt.day, dt.month, dt.weekday()
        wd_cron = (wd + 1) % 7  # Python: Mon=0, Cron: Sun=0

        def matches(field, val, max_val):
            if field == '*': return True
            if field.startswith('*/'):
                step = int(field[2:])
                return val % step == 0
            for part in field.split(','):
                if '-' in part:
                    lo, hi = part.split('-')
                    if int(lo) <= val <= int(hi):
                        return True
                elif int(part) == val:
                    return True
            return False

        if (matches(minute, m, 59) and matches(hour, h, 23) and
            matches(dom, d, 31) and matches(month, mo, 12) and
            matches(dow, wd_cron, 7)):
            runs.append(dt.strftime('%Y-%m-%dT%H:%M:%S'))
            if len(runs) >= count:
                break
        dt += timedelta(minutes=1)
    return runs

entries = []
start = datetime(2024, 3, 15, 12, 0, 0)

with open('$WORKSPACE/crontab.txt') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = line.split(None, 5)
        minute, hour, dom, month, dow = parts[0:5]
        command = parts[5]
        expression = f'{minute} {hour} {dom} {month} {dow}'
        desc = describe_cron(minute, hour, dom, month, dow)
        runs = next_runs_for(minute, hour, dom, month, dow, start)
        entries.append({
            'expression': expression,
            'command': command,
            'description': desc,
            'next_runs': runs
        })

report = {
    'entries': entries,
    'total_entries': len(entries)
}

with open('$WORKSPACE/cron_explained.json', 'w') as f:
    json.dump(report, f, indent=2)
"

echo "Solution written to $WORKSPACE/cron_explained.json"
