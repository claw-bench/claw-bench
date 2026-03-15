#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

python - "$WORKSPACE" << 'PYEOF'
import csv
import sys
from collections import defaultdict

ws = sys.argv[1]

# Load customers
customers = {}
with open(f"{ws}/customers.csv") as f:
    for row in csv.DictReader(f):
        customers[row["customer_id"]] = {"name": row["name"], "region": row["region"]}

# Load products
products = {}
with open(f"{ws}/products.csv") as f:
    for row in csv.DictReader(f):
        products[row["product_id"]] = {"category": row["category"], "unit_price": float(row["unit_price"])}

# Load orders and aggregate
agg = defaultdict(float)
with open(f"{ws}/orders.csv") as f:
    for row in csv.DictReader(f):
        cid = row["customer_id"]
        pid = row["product_id"]
        qty = int(row["quantity"])
        cat = products[pid]["category"]
        price = products[pid]["unit_price"]
        key = (customers[cid]["name"], customers[cid]["region"], cat)
        agg[key] += qty * price

# Sort by revenue descending and write
results = []
for (name, region, cat), rev in agg.items():
    results.append({"customer_name": name, "region": region, "category": cat, "total_revenue": round(rev, 2)})
results.sort(key=lambda x: -x["total_revenue"])

with open(f"{ws}/summary.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["customer_name", "region", "category", "total_revenue"])
    writer.writeheader()
    writer.writerows(results)
PYEOF
