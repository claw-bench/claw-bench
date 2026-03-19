#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

source_dir="$WORKSPACE/source"
translation_dir="$WORKSPACE/translation"
output_file="$WORKSPACE/translation_qa.json"

python3 - <<'EOF'
import os
import json
import math

source_dir = os.environ['WORKSPACE'] + '/source'
translation_dir = os.environ['WORKSPACE'] + '/translation'
output_file = os.environ['WORKSPACE'] + '/translation_qa.json'


def ngram_counts(tokens, n):
    counts = {}
    for i in range(len(tokens) - n + 1):
        ngram = tuple(tokens[i:i+n])
        counts[ngram] = counts.get(ngram, 0) + 1
    return counts


def bleu_like_score(source_text, translation_text):
    source_tokens = source_text.split()
    translation_tokens = translation_text.split()
    precisions = []
    for n in range(1, 5):
        source_ngrams = ngram_counts(source_tokens, n)
        translation_ngrams = ngram_counts(translation_tokens, n)
        if not translation_ngrams:
            precisions.append(0.0)
            continue
        match_count = 0
        total_count = 0
        for ngram, count in translation_ngrams.items():
            match = min(count, source_ngrams.get(ngram, 0))
            match_count += match
            total_count += count
        precision = match_count / total_count if total_count > 0 else 0.0
        precisions.append(precision)
    if any(p == 0 for p in precisions):
        return 0.0
    score = math.exp(sum(math.log(p) for p in precisions) / 4)
    return score


def main():
    files = sorted(f for f in os.listdir(source_dir) if os.path.isfile(os.path.join(source_dir, f)))

    results = {}
    missing_files = []
    added_files = []

    for fname in files:
        source_path = os.path.join(source_dir, fname)
        translation_path = os.path.join(translation_dir, fname)

        if not os.path.isfile(translation_path):
            # If translation missing, treat as all missing segments
            with open(source_path, 'r', encoding='utf-8') as f:
                source_lines = [line.rstrip('\n') for line in f]
            missing_segments = list(range(1, len(source_lines)+1))
            added_segments = []
            bleu_score = 0.0
        else:
            with open(source_path, 'r', encoding='utf-8') as f:
                source_lines = [line.rstrip('\n') for line in f]
            with open(translation_path, 'r', encoding='utf-8') as f:
                translation_lines = [line.rstrip('\n') for line in f]

            source_set = set(source_lines)
            translation_set = set(translation_lines)

            missing_segments = [i+1 for i, line in enumerate(source_lines) if line not in translation_set]
            added_segments = [i+1 for i, line in enumerate(translation_lines) if line not in source_set]

            source_text = ' '.join(source_lines)
            translation_text = ' '.join(translation_lines)

            bleu_score = bleu_like_score(source_text, translation_text)

        results[fname] = {
            "bleu_score": round(bleu_score, 6),
            "missing_segments": missing_segments,
            "added_segments": added_segments
        }

        if missing_segments:
            missing_files.append(fname)
        if added_segments:
            added_files.append(fname)

    overall_score = 0.0
    if results:
        overall_score = sum(info["bleu_score"] for info in results.values()) / len(results)

    output = {
        "files": results,
        "overall_score": round(overall_score, 6),
        "flagged_issues": {
            "missing_segments_files": missing_files,
            "added_segments_files": added_files
        }
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)


if __name__ == '__main__':
    main()
EOF
