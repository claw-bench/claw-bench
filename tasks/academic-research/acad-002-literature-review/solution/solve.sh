#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

python3 - <<EOF
import os; WORKSPACE = os.environ.get('WORKSPACE', os.getcwd())
import json
import csv
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

# Load data
csv_path = Path(f"{WORKSPACE}/abstracts.csv")
paper_ids = []
abstracts = []

with open(csv_path, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        paper_ids.append(row['paper_id'])
        abstracts.append(row['abstract'])

# Compute TF-IDF
vectorizer = TfidfVectorizer(stop_words='english', max_df=0.8, min_df=1)
X = vectorizer.fit_transform(abstracts)

# K-Means clustering
k = 5
model = KMeans(n_clusters=k, random_state=42, n_init=10)
model.fit(X)
labels = model.labels_

# Assign papers to clusters
clusters = {str(i): [] for i in range(k)}
for pid, label in zip(paper_ids, labels):
    clusters[str(label)].append(pid)

# Extract top terms per cluster
terms = vectorizer.get_feature_names_out()
order_centroids = model.cluster_centers_.argsort()[:, ::-1]
top_terms = {}
for i in range(k):
    top_terms[i] = [terms[ind] for ind in order_centroids[i, :10]]

# Generate review outline by joining top terms per cluster
review_outline = [' '.join(top_terms[i]) for i in range(k)]

# Prepare output
output = {
    'clusters': clusters,
    'top_terms': {str(i): top_terms[i] for i in range(k)},
    'review_outline': review_outline
}

# Write output JSON
output_path = Path(f"{WORKSPACE}/topic_clusters.json")
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)
EOF
