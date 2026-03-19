import os
from pathlib import Path
import json
import pytest
from textblob import TextBlob

loaded_language_words = {"radical", "unprecedented", "allegedly", "controversial", "extreme", "biased", "sensational", "propaganda", "manipulative", "exaggerated"}

@pytest.fixture
def workspace(request):
    """Resolve workspace from --workspace CLI option."""
    ws = request.config.getoption("--workspace")
    if ws:
        return Path(ws)
    return Path(os.environ.get("CLAW_WORKSPACE", os.environ.get("WORKSPACE", "workspace")))
@pytest.mark.weight(3)
def test_bias_report_exists(workspace):
    report_path = workspace / "bias_report.json"
    assert report_path.exists(), "bias_report.json file not found"

@pytest.mark.weight(5)
def test_bias_report_structure(workspace):
    report_path = workspace / "bias_report.json"
    with open(report_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Check top-level keys
    assert "articles" in data, "Missing 'articles' key"
    assert "overall_statistics" in data, "Missing 'overall_statistics' key"

    articles = data["articles"]
    assert isinstance(articles, list), "'articles' should be a list"
    assert len(articles) >= 20, "Expected at least 20 articles"

    sources = set()
    bias_scores = []

    for article in articles:
        # Check required keys
        for key in ["filename", "source", "loaded_language_count", "sentiment_polarity", "subjectivity", "bias_score"]:
            assert key in article, f"Article missing key: {key}"

        # Validate types
        assert isinstance(article["filename"], str)
        assert isinstance(article["source"], str)
        assert isinstance(article["loaded_language_count"], int)
        assert isinstance(article["sentiment_polarity"], float) or isinstance(article["sentiment_polarity"], int)
        assert isinstance(article["subjectivity"], float) or isinstance(article["subjectivity"], int)
        assert isinstance(article["bias_score"], float) or isinstance(article["bias_score"], int)

        sources.add(article["source"])
        bias_scores.append(article["bias_score"])

        # Check loaded language count correctness
        # Read article file
        article_path = workspace / "articles" / article["filename"]
        assert article_path.exists(), f"Article file {article["filename"]} not found"
        with open(article_path, "r", encoding="utf-8") as af:
            lines = af.readlines()
        # Skip first line (source)
        text = "".join(lines[1:]).lower()
        count = 0
        for lw in loaded_language_words:
            count += text.count(lw)
        assert count == article["loaded_language_count"], f"Loaded language count mismatch in {article["filename"]}"

        # Check sentiment polarity and subjectivity within valid ranges
        assert -1.0 <= article["sentiment_polarity"] <= 1.0, f"Sentiment polarity out of range in {article["filename"]}"
        assert 0.0 <= article["subjectivity"] <= 1.0, f"Subjectivity out of range in {article["filename"]}"

        # Check bias score calculation
        expected_bias = (article["loaded_language_count"] * 0.5 +
                         abs(article["sentiment_polarity"]) * 2 +
                         article["subjectivity"] * 3)
        # Allow small floating point tolerance
        assert abs(article["bias_score"] - expected_bias) < 1e-5, f"Bias score incorrect in {article["filename"]}"

    # Check overall statistics
    overall = data["overall_statistics"]
    assert "unique_sources" in overall
    assert "average_bias_score" in overall

    assert overall["unique_sources"] == len(sources), "Unique sources count mismatch"

    avg_bias = sum(bias_scores) / len(bias_scores) if bias_scores else 0
    assert abs(overall["average_bias_score"] - avg_bias) < 1e-5, "Average bias score mismatch"
