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

# Generate patient_medications.csv
patients = [f"patient_{i:02d}" for i in range(1, 21)]
medications = [
    "Aspirin", "Warfarin", "Ibuprofen", "Paracetamol", "Metformin", "Lisinopril",
    "Atorvastatin", "Omeprazole", "Simvastatin", "Clopidogrel", "Levothyroxine",
    "Amoxicillin", "Hydrochlorothiazide", "Gabapentin", "Sertraline"
]

# Assign 2-5 medications per patient, no duplicates
patient_meds = {}
for p in patients:
    count = random.randint(2, 5)
    meds = random.sample(medications, count)
    patient_meds[p] = meds

with open(f"{WORKSPACE}/patient_medications.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["patient_id", "medication"])
    for p, meds in patient_meds.items():
        for m in meds:
            writer.writerow([p, m])

# Generate interaction_db.csv
# Create some realistic interactions
interaction_pairs = [
    ("Aspirin", "Warfarin", "high", "Increased risk of bleeding"),
    ("Ibuprofen", "Paracetamol", "low", "Mild stomach upset"),
    ("Metformin", "Lisinopril", "moderate", "Risk of low blood sugar"),
    ("Atorvastatin", "Simvastatin", "high", "Increased risk of muscle damage"),
    ("Omeprazole", "Clopidogrel", "moderate", "Reduced effectiveness of Clopidogrel"),
    ("Levothyroxine", "Amoxicillin", "low", "Reduced absorption of Levothyroxine"),
    ("Hydrochlorothiazide", "Lisinopril", "moderate", "Increased risk of kidney problems"),
    ("Gabapentin", "Sertraline", "moderate", "Increased risk of side effects"),
    ("Warfarin", "Amoxicillin", "high", "Increased bleeding risk"),
    ("Sertraline", "Ibuprofen", "moderate", "Increased risk of bleeding")
]

# Add some reversed pairs to test order independence
interaction_pairs += [(b, a, sev, eff) for (a, b, sev, eff) in interaction_pairs]

with open(f"{WORKSPACE}/interaction_db.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["drug_a", "drug_b", "severity", "effect"])
    for row in interaction_pairs:
        writer.writerow(row)
EOF
