#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

python - "$WORKSPACE" << 'PYEOF'
import sys
import json
import csv
import re

ws = sys.argv[1]

# Read sales CSV
with open(f"{ws}/sales.csv", newline="") as f:
    reader = csv.DictReader(f)
    sales_rows = list(reader)

# Read inventory JSON
with open(f"{ws}/inventory.json") as f:
    inventory = json.load(f)

# Read notes
with open(f"{ws}/notes.txt") as f:
    notes_text = f.read()

# Extract alerts
alerts = []
for line in notes_text.splitlines():
    m = re.match(r"ALERT:\s*(.*)", line)
    if m:
        alerts.append(m.group(1).strip())

# Aggregate sales
all_products = set(inventory.keys())
for row in sales_rows:
    all_products.add(row["product"])

sales_totals = {}
units_sold = {}
for row in sales_rows:
    p = row["product"]
    qty = int(row["quantity"])
    price = float(row["unit_price"])
    sales_totals[p] = sales_totals.get(p, 0.0) + qty * price
    units_sold[p] = units_sold.get(p, 0) + qty

# Build products
products = []
for name in sorted(all_products):
    product_alerts = [a for a in alerts if name in a]
    products.append({
        "name": name,
        "total_sales": round(sales_totals.get(name, 0.0), 2),
        "total_units_sold": units_sold.get(name, 0),
        "stock_level": inventory.get(name, 0),
        "alerts": product_alerts
    })

dashboard = {"products": products}

with open(f"{ws}/dashboard.json", "w") as f:
    json.dump(dashboard, f, indent=2)
PYEOF
