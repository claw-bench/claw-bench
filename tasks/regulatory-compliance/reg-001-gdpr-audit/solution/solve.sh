#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

python3 - <<EOF
import os; WORKSPACE = os.environ.get('WORKSPACE', os.getcwd())
import csv
import json

valid_bases = {"consent", "contract", "legal_obligation", "legitimate_interest", "vital_interest"}

records = []
with open(f"{WORKSPACE}/processing_records.csv", newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        records.append(row)

findings = []
compliant_count = 0
non_compliant_count = 0

for record in records:
    lawful_basis = record["lawful_basis"]
    consent_obtained = record["consent_obtained"].lower()
    third_party_sharing = record["third_party_sharing"].lower()
    try:
        retention_days = int(record["retention_days"])
    except Exception:
        retention_days = -1

    compliant = True

    if lawful_basis not in valid_bases:
        compliant = False
    if lawful_basis == "consent" and consent_obtained != "yes":
        compliant = False
    if retention_days <= 0 or retention_days > 1095:
        compliant = False
    if third_party_sharing == "yes" and lawful_basis not in valid_bases:
        compliant = False

    if compliant:
        compliant_count += 1
    else:
        non_compliant_count += 1

    findings.append({
        "activity": record["activity"],
        "compliant": compliant
    })

# Determine risk level
risk_level = "low"
if non_compliant_count == 0:
    risk_level = "low"
else:
    ratio = non_compliant_count / (compliant_count + non_compliant_count)
    if ratio <= 0.2:
        risk_level = "medium"
    else:
        risk_level = "high"

output = {
    "findings": findings,
    "compliant_count": compliant_count,
    "non_compliant_count": non_compliant_count,
    "risk_level": risk_level
}

with open(f"{WORKSPACE}/gdpr_audit.json", "w", encoding='utf-8') as f:
    json.dump(output, f, indent=2)
EOF
