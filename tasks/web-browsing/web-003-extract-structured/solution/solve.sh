#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${1:-workspace}"

python3 -c "
import json, re

with open('$WORKSPACE/product_page.html') as f:
    html = f.read()

name = re.search(r'class=\"product-name\">(.*?)</h1>', html).group(1)
price_str = re.search(r'class=\"price\">(.*?)</span>', html).group(1)
currency = price_str[0]
price = float(price_str.replace(currency, '').replace(',', ''))
desc = re.search(r'class=\"product-description\">\s*(.*?)\s*</div>', html, re.DOTALL).group(1).strip()
rating = float(re.search(r'class=\"rating-value\">(.*?)</span>', html).group(1))
review_text = re.search(r'class=\"review-count\">(.*?)</span>', html).group(1)
review_count = int(re.search(r'([\d,]+)', review_text).group(1).replace(',', ''))
features = re.findall(r'<li>(.*?)</li>', html[html.index('class=\"features\"'):])
sku = re.search(r'class=\"sku\">SKU:\s*(.*?)</span>', html).group(1).strip()
in_stock = 'In Stock' in re.search(r'class=\"stock-status\">(.*?)</span>', html).group(1)

product = {
    'name': name,
    'price': price,
    'currency': currency,
    'description': desc,
    'rating': rating,
    'review_count': review_count,
    'features': features,
    'in_stock': in_stock,
    'sku': sku
}

with open('$WORKSPACE/product.json', 'w') as f:
    json.dump(product, f, indent=2)
"

echo "Solution written to $WORKSPACE/product.json"
