#!/usr/bin/env bash
# Oracle solution for wfl-002-sequential-task-execution
set -euo pipefail

WORKSPACE="${1:-workspace}"

python3 -c "
import json

with open('$WORKSPACE/tasks.json') as f:
    tasks = json.load(f)

with open('$WORKSPACE/input.txt') as f:
    text = f.read()

# Remove final trailing newline for char count
text_for_chars = text.rstrip('\n')
# Re-read for consistency
lines = text.strip().split('\n')
non_empty_lines = [l for l in lines if l.strip()]

results = []
for i, task in enumerate(tasks):
    name = task['name']
    if name == 'count_lines':
        result = len(non_empty_lines)
    elif name == 'count_words':
        result = sum(len(l.split()) for l in lines)
    elif name == 'count_chars':
        result = len(text_for_chars)
    else:
        raise ValueError(f'Unknown task: {name}')
    results.append({'task': name, 'result': result, 'order': i + 1})

with open('$WORKSPACE/results.json', 'w') as f:
    json.dump(results, f, indent=2)
"

echo "Solution written to $WORKSPACE/results.json"
