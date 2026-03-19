#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

python3 - <<EOF
import os; WORKSPACE = os.environ.get('WORKSPACE', os.getcwd())
import csv
import json

input_path = f"{WORKSPACE}/survey_responses.csv"
output_path = f"{WORKSPACE}/nps_report.json"

# Read data
with open(input_path, newline='', encoding='utf-8') as f:
    reader = list(csv.DictReader(f))

total_responses = len(reader)

# Initialize counts
promoters = 0
passives = 0
detractors = 0

segment_counts = {}
segment_promoters = {}
segment_detractors = {}

for row in reader:
    score = int(row["recommend_0_10"])
    age_group = row["age_group"]

    # Initialize segment counts
    if age_group not in segment_counts:
        segment_counts[age_group] = 0
        segment_promoters[age_group] = 0
        segment_detractors[age_group] = 0

    segment_counts[age_group] += 1

    if score >= 9:
        promoters += 1
        segment_promoters[age_group] += 1
    elif score <= 6:
        detractors += 1
        segment_detractors[age_group] += 1
    else:
        passives += 1

promoter_pct = round(promoters / total_responses * 100, 2) if total_responses > 0 else 0.0
detractor_pct = round(detractors / total_responses * 100, 2) if total_responses > 0 else 0.0
passive_pct = round(passives / total_responses * 100, 2) if total_responses > 0 else 0.0

overall_nps = round(promoter_pct - detractor_pct, 2)

segment_nps = {}
for group in segment_counts:
    count = segment_counts[group]
    if count == 0:
        segment_nps[group] = 0.0
        continue
    p_pct = segment_promoters[group] / count * 100
    d_pct = segment_detractors[group] / count * 100
    segment_nps[group] = round(p_pct - d_pct, 2)

report = {
    "overall_nps": overall_nps,
    "segment_nps": segment_nps,
    "total_responses": total_responses,
    "promoter_pct": promoter_pct,
    "detractor_pct": detractor_pct,
    "passive_pct": passive_pct
}

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2)
EOF
