#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${1:-workspace}"

python3 -c "
import json, glob, os
from collections import Counter
from datetime import datetime

# Load all messages
all_msgs = []
for fpath in sorted(glob.glob('$WORKSPACE/communications/*.json')):
    with open(fpath) as f:
        all_msgs.extend(json.load(f))

# Metrics
per_channel = Counter(m['channel'] for m in all_msgs)
per_user = Counter(m['from'] for m in all_msgs)
timestamps = sorted(m['timestamp'] for m in all_msgs)
replies = sum(1 for m in all_msgs if m.get('subject', '').startswith('Re:'))

start_dt = datetime.fromisoformat(timestamps[0].rstrip('Z'))
end_dt = datetime.fromisoformat(timestamps[-1].rstrip('Z'))
days = max((end_dt - start_dt).days, 1)
avg_per_day = round(len(all_msgs) / days, 1)

metrics = {
    'total_messages': len(all_msgs),
    'per_channel': dict(per_channel),
    'per_user_sent': dict(per_user),
    'busiest_channel': per_channel.most_common(1)[0][0],
    'busiest_user': per_user.most_common(1)[0][0],
    'date_range': {'start': timestamps[0], 'end': timestamps[-1]},
    'avg_messages_per_day': avg_per_day,
    'response_pairs': replies
}

with open('$WORKSPACE/metrics.json', 'w') as f:
    json.dump(metrics, f, indent=2)

# Report
total = len(all_msgs)
lines = ['# Communication Audit Report', '']
lines.append('## Summary')
lines.append(f'- **Total messages**: {total}')
lines.append(f'- **Date range**: {timestamps[0]} to {timestamps[-1]}')
lines.append(f'- **Busiest channel**: {per_channel.most_common(1)[0][0]} ({per_channel.most_common(1)[0][1]} messages)')
lines.append(f'- **Busiest user**: {per_user.most_common(1)[0][0]} ({per_user.most_common(1)[0][1]} messages)')
lines.append('')
lines.append('## Channel Breakdown')
lines.append('| Channel | Messages | Percentage |')
lines.append('| --- | --- | --- |')
for ch, count in sorted(per_channel.items()):
    pct = round(count / total * 100, 1)
    lines.append(f'| {ch} | {count} | {pct}% |')
lines.append('')
lines.append('## Top Senders')
for user, count in per_user.most_common(5):
    lines.append(f'- **{user}**: {count} messages')

with open('$WORKSPACE/audit_report.md', 'w') as f:
    f.write('\n'.join(lines) + '\n')
"

echo "Solution written to $WORKSPACE/"
