#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

python3 - <<EOF
import os; WORKSPACE = os.environ.get('WORKSPACE', os.getcwd())
import csv
import json
from collections import defaultdict

input_csv = f"{WORKSPACE}/emissions_data.csv"
output_json = f"{WORKSPACE}/environmental_report.json"

# Data structures
facility_pollutants = defaultdict(list)  # facility -> list of pollutants data

with open(input_csv, newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        facility = row["facility"]
        pollutant = row["pollutant"]
        amount = float(row["amount_tons"])
        limit = float(row["limit_tons"])
        facility_pollutants[facility].append({
            "pollutant": pollutant,
            "amount_tons": amount,
            "limit_tons": limit,
            "compliance_margin": limit - amount
        })

facility_status = {}
violations = []
total_emissions = {}
compliance_rate = {}

for facility, pollutants in facility_pollutants.items():
    violation_count = 0
    total_amount = 0.0
    total_pollutants = len(pollutants)

    for p in pollutants:
        total_amount += p["amount_tons"]
        if p["amount_tons"] > p["limit_tons"]:
            violation_count += 1
            violations.append({
                "facility": facility,
                "pollutant": p["pollutant"],
                "amount_tons": p["amount_tons"],
                "limit_tons": p["limit_tons"],
                "compliance_margin": round(p["compliance_margin"], 1)
            })

    total_emissions[facility] = round(total_amount, 1)
    compliance_rate_val = 100.0 * (total_pollutants - violation_count) / total_pollutants if total_pollutants > 0 else 100.0
    compliance_rate[facility] = round(compliance_rate_val, 1)
    facility_status[facility] = "Compliant" if violation_count == 0 else "Non-Compliant"

report = {
    "facility_status": facility_status,
    "violations": violations,
    "total_emissions": total_emissions,
    "compliance_rate": compliance_rate
}

with open(output_json, "w") as f:
    json.dump(report, f, indent=2)
EOF
