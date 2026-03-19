#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

mkdir -p "$WORKSPACE"

# Generate market_data.csv with 25 segments
python3 - <<EOF
import os; WORKSPACE = os.environ.get('WORKSPACE', os.getcwd())
import csv
import random
random.seed(42)

segments = [f"Segment_{i}" for i in range(1, 26)]
populations = [random.randint(50000, 500000) for _ in segments]
adoption_rates = [round(random.uniform(0.1, 0.7), 3) for _ in segments]
avg_spends = [round(random.uniform(50, 500), 2) for _ in segments]

with open(f"{WORKSPACE}/market_data.csv", "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["segment", "population", "adoption_rate", "avg_spend"])
    for seg, pop, ar, spend in zip(segments, populations, adoption_rates, avg_spends):
        writer.writerow([seg, pop, ar, spend])
EOF

# Generate company_data.json
python3 - <<EOF
import os; WORKSPACE = os.environ.get('WORKSPACE', os.getcwd())
import json

company_data = {
    "market_share": 0.12,
    "serviceable_regions": ["Segment_1", "Segment_3", "Segment_5", "Segment_7", "Segment_9", "Segment_11", "Segment_13", "Segment_15"],
    "target_segments": ["Segment_3", "Segment_5", "Segment_7"]
}

with open(f"{WORKSPACE}/company_data.json", "w") as f:
    json.dump(company_data, f, indent=2)
EOF
