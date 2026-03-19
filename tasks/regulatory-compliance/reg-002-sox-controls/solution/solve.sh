#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

python3 - <<'EOF'
import csv
import json
import os

controls_path = os.path.join(os.environ.get("CLAW_WORKSPACE", "./"), "controls.csv")
output_path = os.path.join(os.environ.get("CLAW_WORKSPACE", "./"), "sox_assessment.json")

coso_keywords = [
    ("control_environment", ["ethics", "tone at the top", "governance"]),
    ("risk_assessment", ["risk", "assessment", "analysis"]),
    ("control_activities", ["approval", "authorization", "verification", "reconciliation"]),
    ("information_communication", ["communication", "reporting", "information system"]),
    ("monitoring", ["monitor", "audit", "review"])
]

def classify_control(description, ctype):
    desc_lower = description.lower()
    type_lower = ctype.lower()
    for comp, keywords in coso_keywords:
        for kw in keywords:
            if kw in desc_lower or kw in type_lower:
                return comp
    return "control_activities"  # default fallback

def assess_effectiveness(freq, ctype):
    freq_lower = freq.lower()
    ctype_lower = ctype.lower()
    if ctype_lower == "automated":
        return "effective"
    if freq_lower in ["daily", "weekly"]:
        return "effective"
    return "needs_improvement"

results = []
with open(controls_path, newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        cid = row["control_id"]
        desc = row["description"]
        ctype = row["type"]
        freq = row["frequency"]

        coso_comp = classify_control(desc, ctype)
        effectiveness = assess_effectiveness(freq, ctype)

        results.append({
            "control_id": cid,
            "coso_component": coso_comp,
            "effectiveness": effectiveness
        })

with open(output_path, "w") as f:
    json.dump(results, f, indent=2)
EOF
