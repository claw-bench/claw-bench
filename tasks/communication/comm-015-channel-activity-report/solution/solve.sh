#!/usr/bin/env bash
# Oracle solution for comm-015-channel-activity-report
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
mkdir -p "$WORKSPACE"

python - "$WORKSPACE" << 'PYEOF'
import json
import csv
import sys
from collections import Counter
from datetime import datetime

ws = sys.argv[1]

with open(f"{ws}/channels.json", 'r') as f:
    channels = json.load(f)

rows = []
for channel in channels:
    name = channel['name']
    messages = channel['messages']
    total = len(messages)

    authors = [m['author'] for m in messages]
    unique = len(set(authors))

    # Most active author (alphabetically first on tie)
    author_counts = Counter(authors)
    max_count = max(author_counts.values())
    most_active = sorted([a for a, c in author_counts.items() if c == max_count])[0]

    # Peak hour (earliest on tie)
    hours = [datetime.fromisoformat(m['timestamp'].replace('Z', '+00:00')).hour for m in messages]
    hour_counts = Counter(hours)
    max_hour_count = max(hour_counts.values())
    peak_hour = sorted([h for h, c in hour_counts.items() if c == max_hour_count])[0]

    rows.append({
        'channel_name': name,
        'total_messages': total,
        'unique_authors': unique,
        'most_active_author': most_active,
        'peak_hour': peak_hour
    })

rows.sort(key=lambda r: r['channel_name'])

with open(f"{ws}/activity_report.csv", 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['channel_name', 'total_messages', 'unique_authors', 'most_active_author', 'peak_hour'])
    writer.writeheader()
    writer.writerows(rows)
PYEOF

echo "Solution written to $WORKSPACE/activity_report.csv"
