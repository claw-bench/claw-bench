#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE
python3 << 'PYEOF'
import csv, json, os, math
ws = os.environ.get("CLAW_WORKSPACE", "workspace")

# Read data
with open(f"{ws}/customers.csv") as f:
    reader = csv.DictReader(f)
    data = list(reader)

features = ['annual_spending','visit_frequency','avg_transaction','loyalty_years']
X = [[float(r[f]) for f in features] for r in data]

# Min-max normalize
mins = [min(row[i] for row in X) for i in range(4)]
maxs = [max(row[i] for row in X) for i in range(4)]
Xn = [[(row[i]-mins[i])/(maxs[i]-mins[i]) if maxs[i]!=mins[i] else 0 for i in range(4)] for row in X]

# Simple K-Means
import random
random.seed(42)

def kmeans(X, k, max_iter=100):
    centers = random.sample(X, k)
    for _ in range(max_iter):
        clusters = [[] for _ in range(k)]
        labels = []
        for p in X:
            dists = [sum((a-b)**2 for a,b in zip(p,c)) for c in centers]
            label = dists.index(min(dists))
            clusters[label].append(p)
            labels.append(label)
        new_centers = []
        for cl in clusters:
            if cl:
                new_centers.append([sum(p[i] for p in cl)/len(cl) for i in range(len(cl[0]))])
            else:
                new_centers.append(random.choice(X))
        if new_centers == centers:
            break
        centers = new_centers
    inertia = sum(sum((a-b)**2 for a,b in zip(X[i],centers[labels[i]])) for i in range(len(X)))
    return labels, inertia, centers

inertias = {}
all_labels = {}
for k in [3,4,5]:
    labels, inertia, _ = kmeans(Xn, k)
    inertias[str(k)] = round(inertia, 4)
    all_labels[k] = labels

# Pick optimal k (biggest drop)
drops = {k: inertias[str(k-1)] - inertias[str(k)] for k in [4,5]}
optimal_k = max(drops, key=drops.get) if drops[5]/drops[4] < 0.5 else 4
labels = all_labels[optimal_k]

# Profiles
profiles = {}
for seg in range(optimal_k):
    idxs = [i for i,l in enumerate(labels) if l==seg]
    profiles[str(seg)] = {
        "size": len(idxs),
        "avg_spending": round(sum(X[i][0] for i in idxs)/max(len(idxs),1),2),
        "avg_visits": round(sum(X[i][1] for i in idxs)/max(len(idxs),1),2),
        "avg_transaction": round(sum(X[i][2] for i in idxs)/max(len(idxs),1),2),
        "avg_loyalty": round(sum(X[i][3] for i in idxs)/max(len(idxs),1),2),
    }

# Name segments
sorted_segs = sorted(profiles.items(), key=lambda x: x[1]["avg_spending"], reverse=True)
name_templates = ["High-Value Loyal","Active Regular","Budget Conscious","New Explorer","Occasional Visitor"]
seg_names = {seg: name_templates[i] for i,(seg,_) in enumerate(sorted_segs)}

# Write results
with open(f"{ws}/segmentation_results.csv","w",newline="") as f:
    writer = csv.writer(f)
    header = list(data[0].keys()) + ["segment"]
    writer.writerow(header)
    for i,r in enumerate(data):
        writer.writerow(list(r.values()) + [labels[i]])

analysis = {"optimal_k":optimal_k,"inertia_values":inertias,"segment_profiles":profiles,"segment_names":seg_names}
with open(f"{ws}/analysis.json","w") as f:
    json.dump(analysis, f, indent=2)

with open(f"{ws}/report.md","w") as f:
    f.write(f"# Customer Segmentation Report\n\n")
    f.write(f"Optimal clusters: **{optimal_k}**\n\n")
    for seg, profile in profiles.items():
        f.write(f"## Segment {seg}: {seg_names[seg]}\n")
        f.write(f"- Size: {profile['size']} customers\n")
        f.write(f"- Avg Spending: ${profile['avg_spending']:,.2f}\n\n")
PYEOF
