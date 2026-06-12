#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"
export WORKSPACE

python3 - <<'PYEOF'
import os
import json
import csv
import math

workspace = os.environ["WORKSPACE"]
TOL = 1e-9

with open(os.path.join(workspace, "crt_items.json"), encoding="utf-8") as f:
    items = json.load(f)
item_by_id = {it["id"]: it for it in items}
num_items = len(items)

# Read responses.
responses = []
with open(os.path.join(workspace, "responses.csv"), newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        responses.append(
            (row["participant_id"], row["item_id"], float(row["answer"]))
        )


def classify(answer, item):
    if abs(answer - item["correct"]) <= TOL:
        return "correct"
    if abs(answer - item["intuitive"]) <= TOL:
        return "intuitive"
    return "other"


# Per-participant aggregation + per-answer (feature, label) pairs.
participants = {}
labels = []
features = []  # intuitive_count per participant, broadcast to each answer
answer_correct = []  # 1 if this answer correct else 0
per_participant_answers = {}

for pid, item_id, answer in responses:
    item = item_by_id[item_id]
    cls = classify(answer, item)
    p = participants.setdefault(pid, {"crt_score": 0, "intuitive_count": 0})
    if cls == "correct":
        p["crt_score"] += 1
    elif cls == "intuitive":
        p["intuitive_count"] += 1
    per_participant_answers.setdefault(pid, []).append(1 if cls == "correct" else 0)

# Build the answer-level dataset using each participant's intuitive_count.
for pid, answers in per_participant_answers.items():
    ic = participants[pid]["intuitive_count"]
    for y in answers:
        features.append(float(ic))
        answer_correct.append(y)

# Finalize per-participant output.
out_participants = {}
for pid, p in participants.items():
    acc = round(p["crt_score"] / num_items, 3)
    out_participants[pid] = {
        "crt_score": p["crt_score"],
        "intuitive_count": p["intuitive_count"],
        "accuracy": acc,
    }


# Logistic regression fit from scratch (gradient descent) on standardized
# feature for numerical stability, then unscale coefficients back.
def fit_logistic(x, y, iters=20000, lr=0.1):
    n = len(x)
    mean = sum(x) / n
    var = sum((v - mean) ** 2 for v in x) / n
    std = math.sqrt(var) if var > 0 else 1.0
    xs = [(v - mean) / std for v in x]

    w = 0.0
    b = 0.0
    for _ in range(iters):
        gw = 0.0
        gb = 0.0
        for xi, yi in zip(xs, y):
            z = w * xi + b
            pred = 1.0 / (1.0 + math.exp(-z))
            err = pred - yi
            gw += err * xi
            gb += err
        w -= lr * gw / n
        b -= lr * gb / n

    # Unscale: z = w*(x-mean)/std + b = (w/std)*x + (b - w*mean/std)
    coef = w / std
    intercept = b - w * mean / std
    return coef, intercept


coef, intercept = fit_logistic(features, answer_correct)

analysis = {
    "num_items": num_items,
    "participants": out_participants,
    "logistic": {
        "feature": "intuitive_count",
        "coef": round(coef, 3),
        "intercept": round(intercept, 3),
    },
}

with open(os.path.join(workspace, "analysis.json"), "w", encoding="utf-8") as f:
    json.dump(analysis, f, indent=2)
PYEOF
