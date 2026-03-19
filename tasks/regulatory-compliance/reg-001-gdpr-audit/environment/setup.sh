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

activities = [
    "User registration",
    "Newsletter subscription",
    "Order processing",
    "Customer support",
    "Marketing analysis",
    "Payment processing",
    "Employee records management",
    "Website analytics",
    "Third-party advertising",
    "Product reviews",
    "Event registration",
    "Survey data collection",
    "Loyalty program",
    "Fraud detection",
    "Shipping and delivery",
    "Account deletion",
    "Customer feedback",
    "Data backup",
    "Legal compliance",
    "Research and development"
]

data_types = [
    "email",
    "name",
    "address",
    "payment_info",
    "phone_number",
    "ip_address",
    "purchase_history",
    "health_data",
    "location_data",
    "device_id"
]

lawful_bases = ["consent", "contract", "legal_obligation", "legitimate_interest", "vital_interest", "invalid_basis"]

with open(f"{WORKSPACE}/processing_records.csv", "w", newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(["activity", "data_type", "lawful_basis", "retention_days", "consent_obtained", "third_party_sharing"])
    for _ in range(30):
        activity = random.choice(activities)
        data_type = random.choice(data_types)
        lawful_basis = random.choice(lawful_bases)
        # retention_days between 1 and 1500 (some invalid)
        retention_days = random.choice([random.randint(1, 1500), -10, 0])
        consent_obtained = random.choice(["yes", "no"])
        third_party_sharing = random.choice(["yes", "no"])

        # Introduce some realistic patterns
        if lawful_basis != "consent":
            # consent_obtained should be no or yes, but only relevant if lawful_basis is consent
            consent_obtained = "no"
        else:
            # consent obtained mostly yes, sometimes no
            consent_obtained = random.choices(["yes", "no"], weights=[0.8, 0.2])[0]

        writer.writerow([activity, data_type, lawful_basis, retention_days, consent_obtained, third_party_sharing])
EOF
