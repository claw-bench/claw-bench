#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${1:-workspace}"

python3 -c "
import json
from collections import Counter
from datetime import datetime

with open('$WORKSPACE/chat_log.json') as f:
    messages = json.load(f)

user_counts = Counter(m['user'] for m in messages)
hour_counts = Counter(int(m['timestamp'][11:13]) for m in messages)
peak = hour_counts.most_common(1)[0][0]

times = sorted([datetime.fromisoformat(m['timestamp'].rstrip('Z')) for m in messages])
diffs = [(times[i+1] - times[i]).total_seconds() for i in range(len(times)-1)]
avg_rt = round(sum(diffs) / len(diffs))

result = {
    'message_counts': dict(user_counts),
    'hourly_activity': {str(h): c for h, c in sorted(hour_counts.items())},
    'peak_hour': peak,
    'avg_response_time_seconds': avg_rt,
    'most_active_user': user_counts.most_common(1)[0][0],
    'total_messages': len(messages)
}

with open('$WORKSPACE/chat_stats.json', 'w') as f:
    json.dump(result, f, indent=2)
"

echo "Solution written to $WORKSPACE/chat_stats.json"
