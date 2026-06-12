#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

mkdir -p "$WORKSPACE"

python3 - <<'EOF'
import os; WORKSPACE = os.environ.get('WORKSPACE', os.getcwd())
import random
random.seed(42)

# Generate a synthetic commercial lease agreement text with realistic clauses
base_rent = "$5,000 per month"
cam_charges = "$600 per month"
escalation_rate = "3% annually"
lease_term = "5 years"
renewal_options = "Tenant has two 3-year renewal options at market rate."
termination_clauses = "Tenant may terminate after 3 years with 6 months notice and a penalty of 2 months rent."
risk_clauses = [
    "Early termination requires payment of 2 months base rent as penalty.",
    "Tenant responsible for all repairs beyond normal wear and tear.",
    "Landlord may increase CAM charges with 30 days notice.",
]

lines = []
lines.append("COMMERCIAL LEASE AGREEMENT")
lines.append("")
lines.append(f"This Lease Agreement is made for a term of {lease_term}.")
lines.append(f"The Base Rent shall be {base_rent}.")
lines.append(f"Common Area Maintenance (CAM) charges are set at {cam_charges}.")
lines.append(f"An escalation rate of {escalation_rate} applies to the Base Rent annually.")
lines.append("")
lines.append("Renewal Options:")
lines.append(renewal_options)
lines.append("")
lines.append("Termination Clauses:")
lines.append(termination_clauses)
lines.append("")
lines.append("Additional Clauses:")
for clause in risk_clauses:
    lines.append(clause)

# Add some filler clauses
filler_clauses = [
    "Tenant shall maintain insurance coverage as required by law.",
    "Landlord shall provide access to utilities.",
    "No pets allowed on premises.",
    "Tenant must comply with all local regulations.",
    "Security deposit equal to one month’s rent is required.",
    "Landlord responsible for structural repairs.",
    "Tenant shall not sublease without written consent.",
    "Late payment of rent will incur a fee of 5% of the monthly rent.",
    "Landlord may enter premises with 24 hours notice for inspection.",
    "Tenant responsible for all janitorial services inside leased premises.",
    "Any disputes will be resolved by arbitration.",
    "Lease governed by the laws of the state.",
]

random.shuffle(filler_clauses)
lines.extend(filler_clauses[:20])

with open(f"{WORKSPACE}/lease_agreement.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
EOF
