#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

mkdir -p "$WORKSPACE"

python3 - <<EOF
import os; WORKSPACE = os.environ.get('WORKSPACE', os.getcwd())
import csv
import random
random.seed(42)

age_groups = ["18-25", "26-35", "36-45", "46-55", "56+"]
genders = ["Male", "Female", "Other"]

num_rows = 50

with open(f"{WORKSPACE}/survey_responses.csv", "w", newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(["respondent_id", "age_group", "gender", "satisfaction_1_10", "recommend_0_10", "comment"])
    for i in range(1, num_rows + 1):
        respondent_id = f"R{i:03d}"
        age_group = random.choice(age_groups)
        gender = random.choice(genders)
        satisfaction_1_10 = random.randint(1, 10)
        # Generate recommend score with some correlation to satisfaction
        base = satisfaction_1_10
        noise = random.randint(-2, 2)
        recommend_0_10 = min(max(base + noise, 0), 10)
        comment = random.choice([
            "Great product!",
            "Could be better.",
            "I love it.",
            "Not satisfied.",
            "Will recommend to friends.",
            "No comments.",
            "Average experience.",
            "Excellent service.",
            "Needs improvement.",
            ""
        ])
        writer.writerow([respondent_id, age_group, gender, satisfaction_1_10, recommend_0_10, comment])
EOF
