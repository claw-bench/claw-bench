#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${1:-workspace}"

python3 -c "
import json, difflib

with open('$WORKSPACE/v1.txt') as f:
    v1_lines = f.readlines()
with open('$WORKSPACE/v2.txt') as f:
    v2_lines = f.readlines()

sm = difflib.SequenceMatcher(None, v1_lines, v2_lines)

added = []
removed = []
modified = []
unchanged = 0

for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag == 'equal':
        unchanged += (i2 - i1)
    elif tag == 'replace':
        for k in range(max(i2 - i1, j2 - j1)):
            if k < (i2 - i1) and k < (j2 - j1):
                modified.append({
                    'line_number_v1': i1 + k + 1,
                    'line_number_v2': j1 + k + 1,
                    'old_content': v1_lines[i1 + k].rstrip('\n'),
                    'new_content': v2_lines[j1 + k].rstrip('\n')
                })
            elif k < (i2 - i1):
                removed.append({
                    'line_number': i1 + k + 1,
                    'content': v1_lines[i1 + k].rstrip('\n')
                })
            else:
                added.append({
                    'line_number': j1 + k + 1,
                    'content': v2_lines[j1 + k].rstrip('\n')
                })
    elif tag == 'insert':
        for k in range(j1, j2):
            added.append({'line_number': k + 1, 'content': v2_lines[k].rstrip('\n')})
    elif tag == 'delete':
        for k in range(i1, i2):
            removed.append({'line_number': k + 1, 'content': v1_lines[k].rstrip('\n')})

result = {
    'added': added,
    'removed': removed,
    'modified': modified,
    'unchanged_count': unchanged,
    'summary': {
        'total_added': len(added),
        'total_removed': len(removed),
        'total_modified': len(modified),
        'total_unchanged': unchanged
    }
}

with open('$WORKSPACE/changes.json', 'w') as f:
    json.dump(result, f, indent=2)
"

echo "Solution written to $WORKSPACE/changes.json"
