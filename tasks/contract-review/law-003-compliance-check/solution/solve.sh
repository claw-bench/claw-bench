#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

# Use python3 inline to solve the task
python3 - << 'EOF'
import os; WORKSPACE = os.environ.get('WORKSPACE', os.getcwd())
import csv
import json
import re

contract_path = f"{WORKSPACE}/employment_contract.txt"
requirements_path = f"{WORKSPACE}/labor_requirements.csv"
report_path = f"{WORKSPACE}/compliance_report.json"

# Read contract text
with open(contract_path, 'r') as f:
    contract_text = f.read().lower()

# Read requirements
requirements = []
with open(requirements_path, newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        # Store requirement id, description, mandatory
        requirements.append({
            'requirement': row['requirement'],
            'description': row['description'],
            'mandatory': row['mandatory'].strip().lower() == 'true'
        })

# Function to generate keywords from description
# We'll extract words longer than 4 letters and also some common key phrases

def extract_keywords(text):
    # Lowercase and split
    words = re.findall(r'\b[a-z]{5,}\b', text.lower())
    # Add some common phrases manually if possible
    phrases = []
    # For example, split description into words and also include joined words
    # But here just return words
    return set(words + phrases)

compliant_items = []
non_compliant_items = []

for req in requirements:
    keywords = extract_keywords(req['description'])
    # Check if any keyword is in contract text
    # To reduce false positives, require at least one keyword to appear
    if any(kw in contract_text for kw in keywords):
        compliant_items.append(req['requirement'])
    else:
        non_compliant_items.append(req['requirement'])

# Calculate compliance score for mandatory requirements
mandatory_reqs = [r['requirement'] for r in requirements if r['mandatory']]
mandatory_compliant = [r for r in compliant_items if r in mandatory_reqs]

compliance_score = len(mandatory_compliant) / len(mandatory_reqs) if mandatory_reqs else 1.0

report = {
    'compliant_items': compliant_items,
    'non_compliant_items': non_compliant_items,
    'compliance_score': compliance_score
}

with open(report_path, 'w') as f:
    json.dump(report, f, indent=2)
EOF
