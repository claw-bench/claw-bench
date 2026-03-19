#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

python3 - <<EOF
import os; WORKSPACE = os.environ.get('WORKSPACE', os.getcwd())
import csv
import json
import numpy as np

input_file = f"{WORKSPACE}/exam_responses.csv"
item_analysis_file = f"{WORKSPACE}/item_analysis.csv"
summary_file = f"{WORKSPACE}/exam_summary.json"

with open(input_file) as f:
    reader = csv.DictReader(f)
    data = list(reader)

num_students = len(data)
num_items = 30
item_names = [f'item_{i+1}' for i in range(num_items)]

# Extract responses and total scores
item_responses = {item: [] for item in item_names}
total_scores = []
for row in data:
    total_scores.append(float(row['total_score']))
    for item in item_names:
        item_responses[item].append(int(row[item]))

total_scores_np = np.array(total_scores)

# Difficulty (p-value)
difficulties = {item: np.mean(item_responses[item]) for item in item_names}

# Top and bottom 27%
cutoff = int(np.ceil(0.27 * num_students))
sorted_indices = np.argsort(total_scores_np)
bottom_indices = sorted_indices[:cutoff]
top_indices = sorted_indices[-cutoff:]

# Discrimination index
discrimination = {}
for item in item_names:
    responses_np = np.array(item_responses[item])
    top_mean = np.mean(responses_np[top_indices])
    bottom_mean = np.mean(responses_np[bottom_indices])
    discrimination[item] = top_mean - bottom_mean

# Point-biserial correlation
point_biserial = {}
for item in item_names:
    responses_np = np.array(item_responses[item])
    if np.std(responses_np) == 0 or np.std(total_scores_np) == 0:
        corr = 0.0
    else:
        corr = np.corrcoef(responses_np, total_scores_np)[0,1]
    point_biserial[item] = corr

# Write item_analysis.csv
with open(item_analysis_file, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['item', 'difficulty', 'discrimination_index', 'point_biserial'])
    for item in item_names:
        writer.writerow([
            item,
            f'{difficulties[item]:.6f}',
            f'{discrimination[item]:.6f}',
            f'{point_biserial[item]:.6f}'
        ])

# Write exam_summary.json
summary = {
    'num_students': num_students,
    'num_items': num_items,
    'mean_total_score': float(np.mean(total_scores_np)),
    'std_total_score': float(np.std(total_scores_np, ddof=0))
}

with open(summary_file, 'w') as f:
    json.dump(summary, f, indent=2)
EOF
