#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

python3 - <<'EOF'
import os; WORKSPACE = os.environ.get('WORKSPACE', os.getcwd())
import csv
import json
import re

positive_words = ["good", "great", "excellent", "amazing", "love", "wonderful", "best", "fantastic", "perfect", "nice"]
negative_words = ["bad", "terrible", "awful", "worst", "hate", "poor", "disappointing", "boring", "slow", "ugly"]

pos_set = set(positive_words)
neg_set = set(negative_words)

reviews_path = f"{WORKSPACE}/reviews.csv"
output_path = f"{WORKSPACE}/sentiment_dashboard.json"

# Helper to count occurrences of keywords in text (case-insensitive)
def count_keywords(text, keywords):
    # Tokenize words by splitting on non-alphabetic characters
    words = re.findall(r"\b\w+\b", text.lower())
    count = 0
    for w in words:
        if w in keywords:
            count += 1
    return count

# Read reviews
product_stats = {}

with open(reviews_path, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        product = row['product']
        text = row['text']

        pos_count = count_keywords(text, pos_set)
        neg_count = count_keywords(text, neg_set)
        score = pos_count - neg_count

        if score > 0:
            sentiment = 'positive'
        elif score < 0:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'

        if product not in product_stats:
            product_stats[product] = {
                'total_reviews': 0,
                'positive_reviews': 0,
                'negative_reviews': 0,
                'neutral_reviews': 0,
                'sentiment_scores': []
            }

        product_stats[product]['total_reviews'] += 1
        product_stats[product][f'{sentiment}_reviews'] += 1
        product_stats[product]['sentiment_scores'].append(score)

# Prepare output
output = {}
for product, stats in product_stats.items():
    avg_score = sum(stats['sentiment_scores']) / stats['total_reviews']
    output[product] = {
        'total_reviews': stats['total_reviews'],
        'positive_reviews': stats['positive_reviews'],
        'negative_reviews': stats['negative_reviews'],
        'neutral_reviews': stats['neutral_reviews'],
        'average_sentiment_score': avg_score
    }

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)
EOF
