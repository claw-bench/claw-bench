#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

python3 - <<EOF
import os; WORKSPACE = os.environ.get('WORKSPACE', os.getcwd())
import csv
import json

market_data_file = f"{WORKSPACE}/market_data.csv"
company_data_file = f"{WORKSPACE}/company_data.json"
output_file = f"{WORKSPACE}/market_sizing.json"

# Load market data
segments = {}
with open(market_data_file, newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        segment = row["segment"]
        population = int(row["population"])
        adoption_rate = float(row["adoption_rate"])
        avg_spend = float(row["avg_spend"])
        segments[segment] = {
            "population": population,
            "adoption_rate": adoption_rate,
            "avg_spend": avg_spend
        }

# Load company data
with open(company_data_file) as f:
    company_data = json.load(f)

market_share = company_data["market_share"]
serviceable_regions = company_data["serviceable_regions"]

# Calculate TAM (100% adoption all segments)
tam = 0.0
for seg, data in segments.items():
    tam += data["population"] * data["avg_spend"]

# Calculate SAM (adoption rate in serviceable regions)
sam = 0.0
for seg in serviceable_regions:
    data = segments[seg]
    sam += data["population"] * data["adoption_rate"] * data["avg_spend"]

# Calculate SOM
som = sam * market_share

# Round to two decimals
result = {
    "TAM": round(tam, 2),
    "SAM": round(sam, 2),
    "SOM": round(som, 2)
}

# Write output
with open(output_file, "w") as f:
    json.dump(result, f, indent=2)
EOF
