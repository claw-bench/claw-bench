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

# Sample vocabulary for abstracts
topics = {
    'machine learning': ['neural', 'network', 'deep', 'learning', 'model', 'training', 'algorithm', 'data', 'classification', 'accuracy'],
    'graph theory': ['graph', 'node', 'edge', 'network', 'connectivity', 'algorithm', 'path', 'tree', 'cycle', 'vertex'],
    'natural language processing': ['language', 'text', 'model', 'embedding', 'word', 'sentence', 'translation', 'corpus', 'syntax', 'semantics'],
    'computer vision': ['image', 'vision', 'object', 'detection', 'segmentation', 'feature', 'pixel', 'camera', 'recognition', 'video'],
    'robotics': ['robot', 'motion', 'control', 'sensor', 'navigation', 'autonomous', 'path', 'environment', 'manipulation', 'actuator']
}

# Generate 25 papers, 5 per topic
papers = []
paper_id = 1
for topic, words in topics.items():
    for _ in range(5):
        # Create a title
        title = f"Advances in {topic.title()} {random.randint(2000, 2023)}"
        # Create an abstract by sampling words from the topic vocabulary
        abstract_words = random.choices(words, k=50)
        # Add some noise words
        noise_words = ['study', 'results', 'method', 'approach', 'analysis', 'performance', 'evaluation', 'propose', 'experiment']
        abstract_words += random.choices(noise_words, k=10)
        random.shuffle(abstract_words)
        abstract = ' '.join(abstract_words)
        year = random.randint(2000, 2023)
        papers.append({'paper_id': f'P{paper_id:03d}', 'title': title, 'abstract': abstract, 'year': year})
        paper_id += 1

# Write to CSV
with open(f'{WORKSPACE}/abstracts.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['paper_id', 'title', 'abstract', 'year'])
    writer.writeheader()
    for paper in papers:
        writer.writerow(paper)
EOF
