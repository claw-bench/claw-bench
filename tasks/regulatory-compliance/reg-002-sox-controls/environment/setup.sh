#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

mkdir -p "$WORKSPACE"

python3 - <<'EOF'
import os; WORKSPACE = os.environ.get('WORKSPACE', os.getcwd())
import csv
import random
random.seed(42)

controls = []

control_descriptions = [
    "Establishes tone at the top and ethical standards",
    "Performs risk assessment for financial reporting",
    "Approves vendor payments",
    "Communicates financial results to stakeholders",
    "Monitors compliance with internal policies",
    "Reconciles bank statements monthly",
    "Automated system backup",
    "Reviews audit findings",
    "Analyzes risk exposure",
    "Authorizes journal entries",
    "Information system access control",
    "Ethics training for employees",
    "Monthly financial reporting",
    "Quarterly internal audit",
    "Daily transaction verification",
    "Management review of controls",
    "Risk analysis for new products",
    "Automated invoice processing",
    "Communication of control deficiencies",
    "Monitoring of IT general controls"
]

control_types = [
    "manual",
    "automated",
    "manual",
    "manual",
    "automated",
    "manual",
    "automated",
    "manual",
    "manual",
    "manual",
    "automated",
    "manual",
    "manual",
    "manual",
    "manual",
    "manual",
    "manual",
    "automated",
    "manual",
    "manual"
]

frequencies = ["daily", "weekly", "monthly", "quarterly", "annually"]
owners = ["Finance", "Audit", "IT", "Compliance", "Operations"]

for i in range(20):
    control_id = f"C{i+1:03d}"
    description = control_descriptions[i]
    ctype = control_types[i]
    frequency = random.choice(frequencies)
    owner = random.choice(owners)
    controls.append([control_id, description, ctype, frequency, owner])

with open(f"{WORKSPACE}/controls.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["control_id", "description", "type", "frequency", "owner"])
    writer.writerows(controls)
EOF
