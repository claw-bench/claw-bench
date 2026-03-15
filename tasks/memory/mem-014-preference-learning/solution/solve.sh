#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

python - "$WORKSPACE" << 'PYEOF'
import sys, json

ws = sys.argv[1]

interactions = []
with open(f"{ws}/interactions.jsonl") as f:
    for line in f:
        line = line.strip()
        if line:
            interactions.append(json.loads(line))

# Track per category
categories = {}
total_likes = 0
total_dislikes = 0
total_ratings = 0

for inter in interactions:
    cat = inter["category"]
    action = inter["action"]

    if cat not in categories:
        categories[cat] = {"scores": [], "likes": 0, "dislikes": 0, "ratings": 0}

    if action == "liked":
        categories[cat]["scores"].append(1.0)
        categories[cat]["likes"] += 1
        total_likes += 1
    elif action == "disliked":
        categories[cat]["scores"].append(0.0)
        categories[cat]["dislikes"] += 1
        total_dislikes += 1
    elif action == "rated":
        rating = inter["rating"]
        score = (rating - 1) / 4.0
        categories[cat]["scores"].append(score)
        categories[cat]["ratings"] += 1
        total_ratings += 1

# Build category scores
category_scores = {}
for cat in sorted(categories.keys()):
    c = categories[cat]
    avg = round(sum(c["scores"]) / len(c["scores"]), 2)
    category_scores[cat] = {
        "score": avg,
        "interaction_count": len(c["scores"]),
        "likes": c["likes"],
        "dislikes": c["dislikes"],
        "ratings": c["ratings"]
    }

# Top 3 categories
ranked = sorted(category_scores.items(), key=lambda x: (-x[1]["score"], x[0]))
recommended = [name for name, _ in ranked[:3]]

result = {
    "category_scores": category_scores,
    "overall": {
        "total_interactions": len(interactions),
        "total_likes": total_likes,
        "total_dislikes": total_dislikes,
        "total_ratings": total_ratings
    },
    "recommended_categories": recommended
}

with open(f"{ws}/user_profile.json", "w") as f:
    json.dump(result, f, indent=2)
    f.write("\n")
PYEOF
