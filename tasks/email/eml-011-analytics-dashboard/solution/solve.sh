#!/usr/bin/env bash
# Oracle solution for eml-011-analytics-dashboard
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

python3 -c "
import json
from collections import Counter
from datetime import datetime

with open('$WORKSPACE/email_archive.json') as f:
    emails = json.load(f)

# emails_per_day
day_counts = Counter()
for e in emails:
    day = e['date'][:10]
    day_counts[day] += 1

# response_times
mid_to_email = {e['message_id']: e for e in emails}
response_times = []
for e in emails:
    if e['in_reply_to'] and e['in_reply_to'] in mid_to_email:
        parent = mid_to_email[e['in_reply_to']]
        parent_dt = datetime.fromisoformat(parent['date'].replace('Z',''))
        reply_dt = datetime.fromisoformat(e['date'].replace('Z',''))
        diff = (reply_dt - parent_dt).total_seconds() / 60
        if diff > 0:
            response_times.append(diff)

avg_rt = round(sum(response_times) / len(response_times)) if response_times else 0
sorted_rt = sorted(response_times)
med_rt = round(sorted_rt[len(sorted_rt)//2]) if sorted_rt else 0
max_rt = round(max(response_times)) if response_times else 0

# top_contacts
contact_counts = Counter()
for e in emails:
    contact_counts[e['from']] += 1
    contact_counts[e['to']] += 1
top5 = contact_counts.most_common(5)

# busiest_hours
hour_counts = Counter()
for e in emails:
    h = datetime.fromisoformat(e['date'].replace('Z','')).hour
    hour_counts[str(h)] += 1

analytics = {
    'emails_per_day': dict(sorted(day_counts.items())),
    'response_times': {'average_minutes': avg_rt, 'median_minutes': med_rt, 'max_minutes': max_rt},
    'top_contacts': [{'email': email, 'count': count} for email, count in top5],
    'busiest_hours': dict(sorted(hour_counts.items(), key=lambda x: int(x[0])))
}

with open('$WORKSPACE/analytics.json', 'w') as f:
    json.dump(analytics, f, indent=2)
"

echo "Solution written to $WORKSPACE/analytics.json"
