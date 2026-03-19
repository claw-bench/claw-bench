#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

mkdir -p "$WORKSPACE"

python3 - <<EOF
import os; WORKSPACE = os.environ.get('WORKSPACE', os.getcwd())
import csv
import random
random.seed(42)

companies = ["Acme Corp", "Beta Inc", "Gamma LLC", "Delta Co", "Epsilon Ltd"]
products_per_company = 5

with open(f"{WORKSPACE}/products.csv", "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["company", "product", "price", "features_count", "rating", "market_share_pct"])

    for company in companies:
        base_price = random.uniform(50, 500)
        base_features = random.randint(5, 20)
        base_rating = random.uniform(3.0, 5.0)
        base_market_share = random.uniform(5, 40)

        for i in range(products_per_company):
            product_name = f"{company.split()[0]} Product {i+1}"
            # Add some variation
            price = round(base_price * random.uniform(0.8, 1.2), 2)
            features = max(1, int(base_features * random.uniform(0.7, 1.3)))
            rating = round(min(5.0, max(1.0, base_rating * random.uniform(0.85, 1.1))), 2)
            market_share = round(base_market_share * random.uniform(0.7, 1.3), 2)

            writer.writerow([company, product_name, price, features, rating, market_share])
EOF
