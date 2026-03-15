#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
python3 -c "
import csv, json, math

with open('$WORKSPACE/dataset.csv') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

cols = list(rows[0].keys())
data = {c: [float(r[c]) for r in rows] for c in cols}

def pearson(x, y):
    n = len(x)
    mx, my = sum(x)/n, sum(y)/n
    sx = (sum((xi-mx)**2 for xi in x)/n)**0.5
    sy = (sum((yi-my)**2 for yi in y)/n)**0.5
    if sx == 0 or sy == 0:
        return 0.0
    return sum((xi-mx)*(yi-my) for xi, yi in zip(x,y))/(n*sx*sy)

matrix = {}
pairs = []
for i, c1 in enumerate(cols):
    matrix[c1] = {}
    for j, c2 in enumerate(cols):
        r = round(pearson(data[c1], data[c2]), 4)
        matrix[c1][c2] = r
        if i < j:
            pairs.append({'var1': c1, 'var2': c2, 'correlation': r})

with open('$WORKSPACE/correlations.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['variable'] + cols)
    for c1 in cols:
        writer.writerow([c1] + [matrix[c1][c2] for c2 in cols])

pairs.sort(key=lambda x: -abs(x['correlation']))
top3 = pairs[:3]
with open('$WORKSPACE/top_correlations.json', 'w') as f:
    json.dump(top3, f, indent=2)
"
echo "Solution written"
