#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

mkdir -p "$WORKSPACE"

python3 - <<EOF
import os; WORKSPACE = os.environ.get('WORKSPACE', os.getcwd())
import csv
import random
import numpy as np
random.seed(42)
np.random.seed(42)

num_students = 100
num_items = 30

# Simulate abilities from normal distribution
abilities = np.random.normal(loc=0, scale=1, size=num_students)

# Simulate item difficulties from uniform distribution
item_difficulties = np.random.uniform(-1, 1, size=num_items)

# Generate responses using a logistic model for probability of correct
responses = []
for ability in abilities:
    student_responses = []
    for diff in item_difficulties:
        # logistic function
        p_correct = 1 / (1 + np.exp(-(ability - diff)))
        response = 1 if random.random() < p_correct else 0
        student_responses.append(response)
    responses.append(student_responses)

# Calculate total scores
total_scores = [sum(r) for r in responses]

# Write to CSV
header = ['student_id'] + [f'item_{i+1}' for i in range(num_items)] + ['total_score']

with open(f'{WORKSPACE}/exam_responses.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    for i, (resp, total) in enumerate(zip(responses, total_scores)):
        writer.writerow([f'S{i+1}'] + resp + [total])
EOF
