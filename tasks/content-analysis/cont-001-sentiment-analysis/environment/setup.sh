#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

mkdir -p "$WORKSPACE"

python3 - <<'EOF'
import os; WORKSPACE = os.environ.get('WORKSPACE', os.getcwd())
import csv
import random
random.seed(42)

products = ["PhoneX", "LaptopY", "HeadphonesZ", "CameraA", "SpeakerB"]
positive_words = ["good", "great", "excellent", "amazing", "love", "wonderful", "best", "fantastic", "perfect", "nice"]
negative_words = ["bad", "terrible", "awful", "worst", "hate", "poor", "disappointing", "boring", "slow", "ugly"]

# Sample phrases to build reviews
positive_phrases = [
    "I love this product",
    "This is the best purchase",
    "Absolutely fantastic and perfect",
    "Amazing quality and great value",
    "Wonderful experience",
    "Nice and excellent",
    "Highly recommend",
    "Exceeded my expectations",
    "Very good and reliable",
    "Perfect for my needs"
]

negative_phrases = [
    "I hate this product",
    "This is the worst purchase",
    "Absolutely terrible and awful",
    "Bad quality and disappointing",
    "Poor experience",
    "Slow and boring",
    "Not recommended",
    "Did not meet my expectations",
    "Ugly design",
    "Very bad and unreliable"
]

neutral_phrases = [
    "It works as expected",
    "Average product",
    "Nothing special",
    "Okay for the price",
    "Neither good nor bad",
    "Meets basic needs",
    "Standard quality",
    "Satisfactory",
    "Decent",
    "Fair"
]

rows = []
review_id = 1

for product in products:
    # Generate 10-15 reviews per product
    n_reviews = random.randint(20, 25)
    for _ in range(n_reviews):
        rating = random.randint(1, 5)
        # Decide sentiment type roughly correlated with rating
        if rating >= 4:
            phrase = random.choice(positive_phrases)
            # Add some positive words randomly
            extra_pos = random.choices(positive_words, k=random.randint(0,2))
            extra_neg = random.choices(negative_words, k=random.randint(0,1))
        elif rating <= 2:
            phrase = random.choice(negative_phrases)
            extra_pos = random.choices(positive_words, k=random.randint(0,1))
            extra_neg = random.choices(negative_words, k=random.randint(0,2))
        else:
            phrase = random.choice(neutral_phrases)
            extra_pos = random.choices(positive_words, k=random.randint(0,1))
            extra_neg = random.choices(negative_words, k=random.randint(0,1))

        # Construct review text
        words = phrase.split() + extra_pos + extra_neg
        random.shuffle(words)
        text = " ".join(words)

        rows.append({
            "review_id": review_id,
            "product": product,
            "rating": rating,
            "text": text
        })
        review_id += 1

with open(f"{WORKSPACE}/reviews.csv", "w", newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=["review_id", "product", "rating", "text"])
    writer.writeheader()
    writer.writerows(rows)
EOF
