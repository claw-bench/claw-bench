#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

python - "$WORKSPACE" << 'PYEOF'
import sys
import json
import re

ws = sys.argv[1]

with open(f"{ws}/products.html", "r") as f:
    html = f.read()

# Extract tbody content
tbody_match = re.search(r'<tbody>(.*?)</tbody>', html, re.DOTALL)
tbody = tbody_match.group(1)

# Extract rows
rows = re.findall(r'<tr>(.*?)</tr>', tbody, re.DOTALL)

products = []
for row in rows:
    cells = re.findall(r'<td>(.*?)</td>', row)
    name = cells[0]
    price = float(cells[1].replace('$', ''))
    category = cells[2]
    in_stock = cells[3] == "Yes"
    products.append({
        "name": name,
        "price": price,
        "category": category,
        "in_stock": in_stock
    })

# Compute statistics
total = len(products)
avg_price = round(sum(p["price"] for p in products) / total, 2)
categories = {}
for p in products:
    categories[p["category"]] = categories.get(p["category"], 0) + 1
in_stock_count = sum(1 for p in products if p["in_stock"])

result = {
    "products": products,
    "statistics": {
        "total_products": total,
        "avg_price": avg_price,
        "categories": categories,
        "in_stock_count": in_stock_count
    }
}

with open(f"{ws}/products.json", "w") as f:
    json.dump(result, f, indent=2)
PYEOF
