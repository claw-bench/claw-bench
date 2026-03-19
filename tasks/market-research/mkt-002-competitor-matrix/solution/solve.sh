#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

python3 - <<EOF
import os; WORKSPACE = os.environ.get('WORKSPACE', os.getcwd())
import csv
import json
from collections import defaultdict

products_file = f"{WORKSPACE}/products.csv"
matrix_file = f"{WORKSPACE}/competitor_matrix.csv"
summary_file = f"{WORKSPACE}/competitive_summary.json"

# Read products
products = []
with open(products_file, newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        products.append({
            'company': row['company'],
            'product': row['product'],
            'price': float(row['price']),
            'features_count': int(row['features_count']),
            'rating': float(row['rating']),
            'market_share_pct': float(row['market_share_pct'])
        })

# Extract lists for normalization
prices = [p['price'] for p in products]
features = [p['features_count'] for p in products]
ratings = [p['rating'] for p in products]
market_shares = [p['market_share_pct'] for p in products]

# Min-max normalization function
# For price, lower is better, so invert after normalization

def normalize(values, invert=False):
    min_v = min(values)
    max_v = max(values)
    if max_v == min_v:
        # All values same, assign 10
        return [10.0 for _ in values]
    normalized = []
    for v in values:
        norm = (v - min_v) / (max_v - min_v) * 9 + 1  # scale 1 to 10
        if invert:
            norm = 11 - norm  # invert scale
        normalized.append(norm)
    return normalized

price_scores = normalize(prices, invert=True)
feature_scores = normalize(features, invert=False)
rating_scores = normalize(ratings, invert=False)
market_scores = normalize(market_shares, invert=False)

# Attach scores to products
for i, p in enumerate(products):
    p['price_competitiveness'] = price_scores[i]
    p['feature_richness'] = feature_scores[i]
    p['customer_satisfaction'] = rating_scores[i]
    p['market_position'] = market_scores[i]

# Aggregate scores by company (average)
company_scores = defaultdict(lambda: {'price_competitiveness': 0.0,
                                      'feature_richness': 0.0,
                                      'customer_satisfaction': 0.0,
                                      'market_position': 0.0,
                                      'count': 0})

for p in products:
    c = company_scores[p['company']]
    c['price_competitiveness'] += p['price_competitiveness']
    c['feature_richness'] += p['feature_richness']
    c['customer_satisfaction'] += p['customer_satisfaction']
    c['market_position'] += p['market_position']
    c['count'] += 1

for c in company_scores:
    count = company_scores[c]['count']
    for key in ['price_competitiveness', 'feature_richness', 'customer_satisfaction', 'market_position']:
        company_scores[c][key] /= count

# Write competitor_matrix.csv
with open(matrix_file, 'w', newline='') as f:
    fieldnames = ['company', 'price_competitiveness', 'feature_richness', 'customer_satisfaction', 'market_position']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for company, scores in sorted(company_scores.items()):
        row = {'company': company}
        for key in fieldnames[1:]:
            row[key] = round(scores[key], 3)
        writer.writerow(row)

# Prepare competitive_summary.json
summary = {}
criteria = ['price_competitiveness', 'feature_richness', 'customer_satisfaction', 'market_position']
for crit in criteria:
    # Sort companies descending by score
    ranked = sorted(company_scores.items(), key=lambda x: x[1][crit], reverse=True)
    summary[crit] = [c[0] for c in ranked]

with open(summary_file, 'w') as f:
    json.dump(summary, f, indent=2)
EOF
