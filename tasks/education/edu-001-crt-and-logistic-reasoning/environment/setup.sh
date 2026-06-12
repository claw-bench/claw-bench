#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"
export WORKSPACE

# Generate the CRT items and a deterministic set of participant responses.
python3 - <<'PYEOF'
import os
import json
import csv
import random

workspace = os.environ["WORKSPACE"]

# Canonical Frederick (2005) CRT items plus two extended items.
# correct  = reflective correct answer
# intuitive = appealing-but-wrong "lure" answer
items = [
    {"id": "bat_ball",   "correct": 0.05, "intuitive": 0.10},
    {"id": "widgets",    "correct": 5.0,  "intuitive": 100.0},
    {"id": "lily_pads",  "correct": 47.0, "intuitive": 24.0},
    {"id": "students",   "correct": 4.0,  "intuitive": 9.0},
    {"id": "drinks",     "correct": 20.0, "intuitive": 10.0},
]

with open(os.path.join(workspace, "crt_items.json"), "w", encoding="utf-8") as f:
    json.dump(items, f, indent=2)

# Deterministic synthetic participants. Each participant has a latent
# "reflectiveness" that drives the probability of answering each item correctly;
# wrong answers fall back to the intuitive lure most of the time.
random.seed(1234)
num_participants = 40

rows = []
for i in range(1, num_participants + 1):
    pid = f"p{i:02d}"
    reflectiveness = random.uniform(0.0, 1.0)
    for item in items:
        r = random.random()
        if r < reflectiveness:
            ans = item["correct"]
        elif r < reflectiveness + 0.75 * (1 - reflectiveness):
            ans = item["intuitive"]
        else:
            # an "other" answer that is neither correct nor intuitive
            ans = round(item["correct"] + item["intuitive"] + 1.0, 2)
        rows.append((pid, item["id"], ans))

with open(os.path.join(workspace, "responses.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["participant_id", "item_id", "answer"])
    for row in rows:
        w.writerow(row)
PYEOF

echo "Workspace ready at $WORKSPACE"
