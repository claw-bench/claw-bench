#!/usr/bin/env bash
# Oracle solution for wfl-005-parallel-task-fanout
set -euo pipefail

WORKSPACE="${1:-workspace}"

python3 -c "
import json
import os

ws = '$WORKSPACE'
os.makedirs(f'{ws}/results', exist_ok=True)

all_results = []

for i in range(1, 6):
    with open(f'{ws}/items/item_{i}.json') as f:
        item = json.load(f)

    # Validate
    required = {'id', 'name', 'value', 'category', 'tags'}
    valid = required.issubset(set(item.keys()))

    # Transform
    normalized = min((item['value'] / 1000) * 100, 100)
    label = item['name'].upper()

    # Score
    score = round(normalized * (1 + 0.1 * len(item['tags'])), 2)

    result = {
        **item,
        'valid': valid,
        'normalized': normalized,
        'label': label,
        'score': score
    }

    with open(f'{ws}/results/result_{i}.json', 'w') as f:
        json.dump(result, f, indent=2)

    all_results.append(result)

# Aggregate
scores = [r['score'] for r in all_results]
valid_count = sum(1 for r in all_results if r['valid'])
highest = max(all_results, key=lambda r: r['score'])

aggregated = {
    'items': all_results,
    'summary': {
        'total_items': len(all_results),
        'valid_count': valid_count,
        'total_score': round(sum(scores), 2),
        'average_score': round(sum(scores) / len(scores), 2),
        'highest_scorer': highest['id']
    }
}

with open(f'{ws}/aggregated_results.json', 'w') as f:
    json.dump(aggregated, f, indent=2)
"

echo "Solution written to $WORKSPACE/results/ and $WORKSPACE/aggregated_results.json"
