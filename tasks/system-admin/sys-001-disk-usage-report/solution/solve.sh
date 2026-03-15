#!/usr/bin/env bash
# Oracle solution for sys-001-disk-usage-report
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

python3 -c "
import json, re

def parse_size(s):
    s = s.strip()
    units = {'K': 1024, 'M': 1024**2, 'G': 1024**3, 'T': 1024**4}
    match = re.match(r'^([\d.]+)([KMGT])$', s)
    if match:
        return float(match.group(1)) * units[match.group(2)]
    return float(s)

def human_readable(b):
    for unit in ['B', 'K', 'M', 'G', 'T']:
        if b < 1024:
            return f'{b:.1f}{unit}' if unit != 'B' else f'{int(b)}B'
        b /= 1024
    return f'{b:.1f}P'

entries = []
with open('$WORKSPACE/filesystem.txt') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        parts = line.split('\t')
        size_str = parts[0]
        path = parts[1]
        size_bytes = int(parse_size(size_str))
        entries.append({'path': path, 'size_bytes': size_bytes, 'size_human': size_str})

total = sum(e['size_bytes'] for e in entries)
sorted_entries = sorted(entries, key=lambda x: x['size_bytes'], reverse=True)
top5 = sorted_entries[:5]
over_1gb = [e for e in sorted_entries if e['size_bytes'] >= 1073741824]

report = {
    'total_size_bytes': total,
    'total_size_human': human_readable(total),
    'top_5_largest': top5,
    'dirs_over_1gb': over_1gb,
    'dir_count': len(entries)
}

with open('$WORKSPACE/report.json', 'w') as f:
    json.dump(report, f, indent=2)
"

echo "Solution written to $WORKSPACE/report.json"
