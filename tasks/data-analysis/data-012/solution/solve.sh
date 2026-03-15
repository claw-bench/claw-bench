#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
python3 -c "
import csv, json

with open('${WORKSPACE}/historical.csv') as f:
    reader = csv.DictReader(f)
    data = [(float(r['x']), float(r['y'])) for r in reader]

xs = [d[0] for d in data]
ys = [d[1] for d in data]
n = len(xs)
mean_x = sum(xs) / n
mean_y = sum(ys) / n

ss_xy = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
ss_xx = sum((x - mean_x)**2 for x in xs)
slope = ss_xy / ss_xx
intercept = mean_y - slope * mean_x

y_pred = [slope * x + intercept for x in xs]
ss_res = sum((y - yp)**2 for y, yp in zip(ys, y_pred))
ss_tot = sum((y - mean_y)**2 for y in ys)
r_squared = 1 - ss_res / ss_tot
mse = ss_res / n

model = {
    'slope': round(slope, 4),
    'intercept': round(intercept, 4),
    'r_squared': round(r_squared, 4),
    'mse': round(mse, 4)
}
with open('${WORKSPACE}/model.json', 'w') as f:
    json.dump(model, f, indent=2)

max_x = max(xs)
predictions = []
for x in [max_x + 1, max_x + 2, max_x + 3]:
    py = round(slope * x + intercept, 2)
    predictions.append({'x': int(x), 'predicted_y': py})

with open('${WORKSPACE}/predictions.json', 'w') as f:
    json.dump(predictions, f, indent=2)
"
echo "Solution written"
