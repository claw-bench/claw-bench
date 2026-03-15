#!/usr/bin/env bash
# Oracle solution for sys-004-log-analysis
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

python3 -c "
import json, re
from collections import Counter, defaultdict

entries = []
with open('$WORKSPACE/syslog.txt') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        match = re.match(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (INFO|WARNING|ERROR|CRITICAL) (\w+): (.+)$', line)
        if match:
            entries.append({
                'timestamp': match.group(1),
                'severity': match.group(2),
                'source': match.group(3),
                'message': match.group(4)
            })

severity_counts = Counter(e['severity'] for e in entries)
error_sources = Counter()
for e in entries:
    if e['severity'] in ('ERROR', 'CRITICAL'):
        error_sources[e['source']] += 1

top_error_sources = [
    {'source': s, 'error_count': c}
    for s, c in error_sources.most_common(5)
]

hour_counts = Counter()
for e in entries:
    hour = int(e['timestamp'].split(' ')[1].split(':')[0])
    hour_counts[hour] += 1

peak_hour = hour_counts.most_common(1)[0][0]
entries_per_hour = {str(h): c for h, c in sorted(hour_counts.items())}

critical_entries = [
    {'timestamp': e['timestamp'], 'source': e['source'], 'message': e['message']}
    for e in entries if e['severity'] == 'CRITICAL'
]

report = {
    'total_entries': len(entries),
    'severity_counts': {
        'INFO': severity_counts.get('INFO', 0),
        'WARNING': severity_counts.get('WARNING', 0),
        'ERROR': severity_counts.get('ERROR', 0),
        'CRITICAL': severity_counts.get('CRITICAL', 0)
    },
    'top_error_sources': top_error_sources,
    'peak_hour': peak_hour,
    'entries_per_hour': entries_per_hour,
    'critical_entries': critical_entries
}

with open('$WORKSPACE/log_analysis.json', 'w') as f:
    json.dump(report, f, indent=2)
"

echo "Solution written to $WORKSPACE/log_analysis.json"
