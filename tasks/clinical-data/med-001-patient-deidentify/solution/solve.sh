#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE
mkdir -p "$WORKSPACE/deidentified" "$WORKSPACE/archive"
python3 << PYEOF
import csv, json, os
from datetime import datetime
ws = os.environ.get("CLAW_WORKSPACE", "$WORKSPACE")
with open(f"{ws}/patient_records.csv") as f:
    reader = csv.DictReader(f)
    rows = list(reader)
clean = []
audit = ["De-identification Audit Log", f"Processed: {len(rows)} records", ""]
for i, r in enumerate(rows):
    pid = f"P{i+1:03d}"
    year = int(r["dob"].split("-")[0])
    age = 2025 - year
    decade = (age // 10) * 10
    age_range = f"{decade}-{decade+9}"
    clean.append({"patient_id":pid,"age_range":age_range,"state":r["state"],
                  "diagnosis":r["diagnosis"],"systolic_bp":r["systolic_bp"],
                  "diastolic_bp":r["diastolic_bp"],"glucose_mg_dl":r["glucose_mg_dl"],
                  "cholesterol_mg_dl":r["cholesterol_mg_dl"]})
    audit.append(f"Record {i+1}: name->'{pid}', dob->'{age_range}', ssn->REMOVED, address->REMOVED(kept state)")
with open(f"{ws}/deidentified/patients_clean.csv","w",newline="") as f:
    w = csv.DictWriter(f, fieldnames=clean[0].keys())
    w.writeheader()
    w.writerows(clean)
# Statistics
diag_freq = {}
diag_vals = {}
age_dist = {}
for r in clean:
    diag_freq[r["diagnosis"]] = diag_freq.get(r["diagnosis"],0)+1
    age_dist[r["age_range"]] = age_dist.get(r["age_range"],0)+1
    if r["diagnosis"] not in diag_vals:
        diag_vals[r["diagnosis"]] = {"sbp":[],"dbp":[],"glucose":[],"chol":[]}
    diag_vals[r["diagnosis"]]["sbp"].append(int(r["systolic_bp"]))
    diag_vals[r["diagnosis"]]["dbp"].append(int(r["diastolic_bp"]))
    diag_vals[r["diagnosis"]]["glucose"].append(int(r["glucose_mg_dl"]))
    diag_vals[r["diagnosis"]]["chol"].append(int(r["cholesterol_mg_dl"]))
avg_vals = {}
for d,v in diag_vals.items():
    avg_vals[d] = {k:round(sum(vals)/len(vals),1) for k,vals in v.items()}
stats = {"total_patients":len(clean),"age_distribution":age_dist,"diagnosis_frequency":diag_freq,"avg_lab_values_by_diagnosis":avg_vals}
with open(f"{ws}/deidentified/statistics.json","w") as f:
    json.dump(stats,f,indent=2)
os.rename(f"{ws}/patient_records.csv", f"{ws}/archive/original_records.csv.bak")
with open(f"{ws}/deidentified/audit_log.txt","w") as f:
    f.write("\n".join(audit))
PYEOF
