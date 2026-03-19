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

facilities = ["FacilityA", "FacilityB", "FacilityC", "FacilityD", "FacilityE"]
pollutants = ["NOx", "SO2", "CO2", "PM2.5", "VOC"]

rows = []
for facility in facilities:
    for pollutant in pollutants:
        limit = round(random.uniform(50, 150), 1)
        # amount is sometimes above limit to create violations
        if random.random() < 0.3:
            amount = round(limit + random.uniform(1, 50), 1)
        else:
            amount = round(random.uniform(0, limit), 1)
        rows.append([facility, pollutant, amount, limit])

with open(f"{WORKSPACE}/emissions_data.csv", "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["facility", "pollutant", "amount_tons", "limit_tons"])
    writer.writerows(rows)
EOF
