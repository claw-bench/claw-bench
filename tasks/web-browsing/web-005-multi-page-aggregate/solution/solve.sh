#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${1:-workspace}"

python3 -c "
import json, re, glob, os

products = []
for fpath in sorted(glob.glob('$WORKSPACE/pages/page*.html')):
    fname = os.path.basename(fpath)
    with open(fpath) as f:
        html = f.read()
    for m in re.finditer(r'<div class=\"product\">(.*?)</div>', html, re.DOTALL):
        block = m.group(1)
        name = re.search(r'class=\"product-name\">(.*?)</h3>', block).group(1)
        price = float(re.search(r'class=\"price\">\\\$([\d.]+)</span>', block).group(1))
        category = re.search(r'class=\"category\">(.*?)</span>', block).group(1)
        rating = float(re.search(r'class=\"rating\">([\d.]+)</span>', block).group(1))
        products.append({
            'name': name,
            'price': price,
            'category': category,
            'rating': rating,
            'source_page': fname
        })

prices = [p['price'] for p in products]
ratings = [p['rating'] for p in products]

result = {
    'products': products,
    'total_products': len(products),
    'price_range': {'min': min(prices), 'max': max(prices)},
    'categories': sorted(set(p['category'] for p in products)),
    'avg_rating': round(sum(ratings) / len(ratings), 2)
}

with open('$WORKSPACE/aggregated.json', 'w') as f:
    json.dump(result, f, indent=2)
"

echo "Solution written to $WORKSPACE/aggregated.json"
