import os
from pathlib import Path
import json
import pytest

@pytest.fixture
def workspace(request):
    """Resolve workspace from --workspace CLI option."""
    ws = request.config.getoption("--workspace")
    if ws:
        return Path(ws)
    return Path(os.environ.get("CLAW_WORKSPACE", os.environ.get("WORKSPACE", "workspace")))
@pytest.mark.weight(3)
def test_sentiment_dashboard_exists(workspace):
    output_file = workspace / "sentiment_dashboard.json"
    assert output_file.exists(), "Output file sentiment_dashboard.json does not exist"

@pytest.mark.weight(5)
def test_sentiment_dashboard_content(workspace):
    output_file = workspace / "sentiment_dashboard.json"
    with open(output_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Check that data is a dict
    assert isinstance(data, dict), "Output JSON should be a dictionary keyed by product"

    # Check keys correspond to expected products
    expected_products = {"PhoneX", "LaptopY", "HeadphonesZ", "CameraA", "SpeakerB"}
    assert expected_products.issubset(data.keys()), "Output missing some expected products"

    for product, stats in data.items():
        # Check required keys
        for key in ["total_reviews", "positive_reviews", "negative_reviews", "neutral_reviews", "average_sentiment_score"]:
            assert key in stats, f"Missing key {key} in product {product}"

        # Check counts are integers and non-negative
        assert isinstance(stats["total_reviews"], int) and stats["total_reviews"] > 0
        assert isinstance(stats["positive_reviews"], int) and stats["positive_reviews"] >= 0
        assert isinstance(stats["negative_reviews"], int) and stats["negative_reviews"] >= 0
        assert isinstance(stats["neutral_reviews"], int) and stats["neutral_reviews"] >= 0

        # Check sum of sentiment counts equals total_reviews
        total = stats["positive_reviews"] + stats["negative_reviews"] + stats["neutral_reviews"]
        assert total == stats["total_reviews"], f"Sentiment counts do not sum to total_reviews for {product}"

        # Check average_sentiment_score is float
        assert isinstance(stats["average_sentiment_score"], float)

@pytest.mark.weight(2)
def test_sentiment_scores_consistency(workspace):
    import csv

    reviews_file = workspace / "reviews.csv"
    output_file = workspace / "sentiment_dashboard.json"

    positive_words = {"good", "great", "excellent", "amazing", "love", "wonderful", "best", "fantastic", "perfect", "nice"}
    negative_words = {"bad", "terrible", "awful", "worst", "hate", "poor", "disappointing", "boring", "slow", "ugly"}

    # Read reviews
    reviews = []
    with open(reviews_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            reviews.append(row)

    # Load output
    with open(output_file, "r", encoding="utf-8") as f:
        dashboard = json.load(f)

    # Compute sentiment scores per review
    per_product_scores = {}
    per_product_counts = {}
    for r in reviews:
        product = r["product"]
        text = r["text"].lower()
        pos_count = sum(text.count(w) for w in positive_words)
        neg_count = sum(text.count(w) for w in negative_words)
        score = pos_count - neg_count

        sentiment = "neutral"
        if score > 0:
            sentiment = "positive"
        elif score < 0:
            sentiment = "negative"

        if product not in per_product_scores:
            per_product_scores[product] = []
            per_product_counts[product] = {"positive":0, "negative":0, "neutral":0}

        per_product_scores[product].append(score)
        per_product_counts[product][sentiment] += 1

    # Verify counts and average scores match output
    for product, scores in per_product_scores.items():
        stats = dashboard.get(product)
        assert stats is not None, f"Product {product} missing in output"

        assert stats["total_reviews"] == len(scores), f"Total reviews mismatch for {product}"
        assert stats["positive_reviews"] == per_product_counts[product]["positive"], f"Positive reviews count mismatch for {product}"
        assert stats["negative_reviews"] == per_product_counts[product]["negative"], f"Negative reviews count mismatch for {product}"
        assert stats["neutral_reviews"] == per_product_counts[product]["neutral"], f"Neutral reviews count mismatch for {product}"

        avg_score = sum(scores) / len(scores)
        # Allow small floating point difference
        assert abs(stats["average_sentiment_score"] - avg_score) < 1e-6, f"Average sentiment score mismatch for {product}"
