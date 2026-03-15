#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

python - "$WORKSPACE" << 'PYEOF'
import csv, json, os, re, sys

ws = sys.argv[1]

# Parse TOML manually (avoid import issues)
rules_text = open(os.path.join(ws, 'rules.toml')).read()
# Simple TOML parsing for our known structure

price_adj = float(re.search(r'price_adjustment\s*=\s*([\d.]+)', rules_text).group(1))
min_price = float(re.search(r'min_price\s*=\s*([\d.]+)', rules_text).group(1))

exc_match = re.search(r'exclude_categories\s*=\s*\[([^\]]+)\]', rules_text)
exclude_categories = [s.strip().strip('"') for s in exc_match.group(1).split(',')]

tag_match = re.search(r'tag_required\s*=\s*\[([^\]]+)\]', rules_text)
tag_required = [s.strip().strip('"') for s in tag_match.group(1).split(',')]

# Load products
products = []
with open(os.path.join(ws, 'products.csv')) as f:
    reader = csv.DictReader(f)
    for row in reader:
        products.append(row)

# Load discounts
with open(os.path.join(ws, 'discounts.json')) as f:
    discounts = json.load(f)

# Load tags
tags_map = {}
with open(os.path.join(ws, 'tags.txt')) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        pid_str, tag_str = line.split(':', 1)
        tags_map[int(pid_str)] = [t.strip() for t in tag_str.split(',')]

result = []
for p in products:
    pid = int(p['id'])
    category = p['category']
    base_price = float(p['base_price'])
    name = p['name']

    # Exclude categories
    if category in exclude_categories:
        continue

    # Get tags
    product_tags = tags_map.get(pid, [])

    # Tag filter
    if tag_required:
        if not any(t in tag_required for t in product_tags):
            continue

    discount_pct = discounts.get(category, 0)
    final = base_price * (1 - discount_pct / 100.0) * price_adj
    final = max(final, min_price)
    final = round(final, 2)

    result.append({
        'id': pid,
        'name': name,
        'category': category,
        'original_price': base_price,
        'discount_percent': discount_pct,
        'final_price': final,
        'tags': product_tags
    })

result.sort(key=lambda x: x['id'])

with open(os.path.join(ws, 'result.json'), 'w') as f:
    json.dump(result, f, indent=2)
PYEOF
