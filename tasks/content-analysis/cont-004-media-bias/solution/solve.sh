#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

# Use python3 inline to process articles and generate bias_report.json
python3 - <<EOF
import json
import os
from pathlib import Path
from textblob import TextBlob

loaded_language_words = {"radical", "unprecedented", "allegedly", "controversial", "extreme", "biased", "sensational", "propaganda", "manipulative", "exaggerated"}

articles_dir = Path(os.path.join(os.environ.get("CLAW_WORKSPACE", "./"), "articles"))
output_file = Path(os.path.join(os.environ.get("CLAW_WORKSPACE", "./"), "bias_report.json"))

articles_data = []
sources_set = set()

for article_file in sorted(articles_dir.glob("*.txt")):
    with open(article_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
    if not lines:
        continue
    # Extract source
    first_line = lines[0].strip()
    if not first_line.lower().startswith("source:"):
        source = "Unknown"
        text_lines = lines
    else:
        source = first_line[7:].strip()
        text_lines = lines[1:]

    text = "".join(text_lines).strip()
    text_lower = text.lower()

    # Count loaded language
    loaded_count = 0
    for lw in loaded_language_words:
        loaded_count += text_lower.count(lw)

    # Sentiment and subjectivity
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity

    # Bias score
    bias_score = loaded_count * 0.5 + abs(polarity) * 2 + subjectivity * 3

    articles_data.append({
        "filename": article_file.name,
        "source": source,
        "loaded_language_count": loaded_count,
        "sentiment_polarity": polarity,
        "subjectivity": subjectivity,
        "bias_score": bias_score
    })
    sources_set.add(source)

# Overall statistics
unique_sources = len(sources_set)
avg_bias_score = sum(a["bias_score"] for a in articles_data) / len(articles_data) if articles_data else 0

report = {
    "articles": articles_data,
    "overall_statistics": {
        "unique_sources": unique_sources,
        "average_bias_score": avg_bias_score
    }
}

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)
EOF
