#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

python3 - << EOF
import os
import json
import csv
import re

workspace = os.environ.get("CLAW_WORKSPACE", "$WORKSPACE")
rubric_path = os.path.join(workspace, "rubric.csv")
essays_dir = os.path.join(workspace, "essays")
grades_path = os.path.join(workspace, "grades.json")
english_words_path = os.path.join(workspace, "english_words.txt")

# Load rubric
rubric = {}
with open(rubric_path, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        criterion = row['criterion']
        max_points = float(row['max_points'])
        keywords = [kw.strip().lower() for kw in row['keywords'].split(';') if kw.strip()]
        rubric[criterion] = {
            'max_points': max_points,
            'keywords': keywords
        }

# Load english words
with open(english_words_path, 'r', encoding='utf-8') as f:
    english_words = set(line.strip().lower() for line in f if line.strip())

# Helper functions

def tokenize(text):
    return re.findall(r"\b\w+\b", text.lower())

def count_spelling_errors(words):
    return sum(1 for w in words if w not in english_words)

def average_sentence_length(text):
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    words = tokenize(text)
    if not sentences:
        return 0
    return len(words) / len(sentences)

# Score calculation function
# Combines keyword presence and text quality
# Keyword presence fraction weighted 0.6
# Text quality weighted 0.4
# Text quality: average sentence length (optimal between 10 and 20 words) and spelling errors

def score_criterion(text, criterion_info):
    keywords = criterion_info['keywords']
    max_points = criterion_info['max_points']

    text_lower = text.lower()

    # Keyword presence
    keyword_hits = 0
    for kw in keywords:
        pattern = re.compile(rf'\b{re.escape(kw)}\b', re.IGNORECASE)
        if pattern.search(text_lower):
            keyword_hits += 1
    keyword_fraction = keyword_hits / len(keywords) if keywords else 0

    # Text quality
    avg_sent_len = average_sentence_length(text)
    words = tokenize(text)
    spelling_errors = count_spelling_errors(words)

    # Sentence length score: 0 if <5 or >25, linear max at 15
    if avg_sent_len < 5 or avg_sent_len > 25:
        sent_len_score = 0
    else:
        # Max score at 15 words
        sent_len_score = 1 - abs(avg_sent_len - 15) / 10  # between 0 and 1
        sent_len_score = max(0, sent_len_score)

    # Spelling score: max 1, decrease by 0.05 per error, min 0
    spelling_score = max(0, 1 - 0.05 * spelling_errors)

    text_quality_score = (sent_len_score + spelling_score) / 2  # average

    # Combine
    combined_score = 0.6 * keyword_fraction + 0.4 * text_quality_score

    final_score = combined_score * max_points

    # Clamp and round
    final_score = max(0, min(final_score, max_points))
    return round(final_score, 1)

# Process all essays
grades = {}
for filename in os.listdir(essays_dir):
    if not filename.endswith('.txt'):
        continue
    student_id = filename[:-4]
    essay_path = os.path.join(essays_dir, filename)
    with open(essay_path, 'r', encoding='utf-8') as f:
        text = f.read()

    student_scores = {}
    for criterion, info in rubric.items():
        score = score_criterion(text, info)
        student_scores[criterion] = score
    grades[student_id] = student_scores

# Write grades.json
with open(grades_path, 'w', encoding='utf-8') as f:
    json.dump(grades, f, indent=2)
EOF
