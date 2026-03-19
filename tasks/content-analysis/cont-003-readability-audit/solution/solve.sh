#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

# Python solution to compute readability metrics
python3 - <<'EOF'
import os
import re
import csv

DOCS_DIR = os.path.join(os.environ.get("WORKSPACE", ""), "documents")
OUTPUT_FILE = os.path.join(os.environ.get("WORKSPACE", ""), "readability_report.csv")

# Sentence splitter regex: split on . ! ? followed by space or EOL
sentence_split_re = re.compile(r'[.!?]+\s+')

# Word tokenizer: sequences of alphabetic characters
word_re = re.compile(r"[A-Za-z]+")

vowels = "aeiouy"


def count_syllables(word):
    word = word.lower()
    if len(word) <= 3:
        return 1
    # Count vowel groups as syllables
    syllables = 0
    prev_char_was_vowel = False
    for char in word:
        is_vowel = char in vowels
        if is_vowel and not prev_char_was_vowel:
            syllables += 1
        prev_char_was_vowel = is_vowel
    # Remove silent e
    if word.endswith("e") and syllables > 1:
        syllables -= 1
    return max(syllables, 1)


def is_complex_word(word):
    # Complex word: 3 or more syllables
    # Exclude proper nouns (capitalized not at start), but we treat all lowercase words
    # We do not exclude jargon or compound words for simplicity
    return count_syllables(word) >= 3


def flesch_kincaid(total_words, total_sentences, total_syllables):
    if total_sentences == 0 or total_words == 0:
        return 0.0
    return 0.39 * (total_words / total_sentences) + 11.8 * (total_syllables / total_words) - 15.59


def gunning_fog(total_words, total_sentences, complex_words):
    if total_sentences == 0 or total_words == 0:
        return 0.0
    return 0.4 * ((total_words / total_sentences) + 100 * (complex_words / total_words))


def coleman_liau(total_letters, total_sentences, total_words):
    if total_words == 0:
        return 0.0
    L = (total_letters / total_words) * 100
    S = (total_sentences / total_words) * 100
    return 0.0588 * L - 0.296 * S - 15.8


def analyze_text(text):
    # Split sentences
    sentences = sentence_split_re.split(text.strip())
    sentences = [s.strip() for s in sentences if s.strip()]

    total_sentences = len(sentences)
    total_words = 0
    total_syllables = 0
    complex_words = 0
    total_letters = 0

    sentence_word_counts = []
    word_lengths = []

    for sentence in sentences:
        words = word_re.findall(sentence)
        sentence_word_counts.append(len(words))
        for w in words:
            total_words += 1
            sylls = count_syllables(w)
            total_syllables += sylls
            if is_complex_word(w):
                complex_words += 1
            total_letters += len(w)
            word_lengths.append(len(w))

    if total_sentences == 0 or total_words == 0:
        return 0, 0, 0, 0, 0

    fk = flesch_kincaid(total_words, total_sentences, total_syllables)
    fog = gunning_fog(total_words, total_sentences, complex_words)
    cli = coleman_liau(total_letters, total_sentences, total_words)
    avg_sentence_length = sum(sentence_word_counts) / total_sentences if total_sentences else 0
    avg_word_length = sum(word_lengths) / total_words if total_words else 0

    return fk, fog, cli, avg_sentence_length, avg_word_length


def main():
    files = [f for f in os.listdir(DOCS_DIR) if f.endswith(".txt")]
    results = []
    for filename in sorted(files):
        path = os.path.join(DOCS_DIR, filename)
        with open(path, encoding="utf-8") as f:
            text = f.read()
        fk, fog, cli, asl, awl = analyze_text(text)
        results.append({
            "document": filename,
            "fk_grade": round(fk, 2),
            "fog_index": round(fog, 2),
            "cli": round(cli, 2),
            "avg_sentence_length": round(asl, 2),
            "avg_word_length": round(awl, 2),
        })

    with open(OUTPUT_FILE, "w", newline='', encoding="utf-8") as csvfile:
        fieldnames = ["document", "fk_grade", "fog_index", "cli", "avg_sentence_length", "avg_word_length"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)


if __name__ == "__main__":
    main()
EOF
