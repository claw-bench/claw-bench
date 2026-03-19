#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

mkdir -p "$WORKSPACE/articles"

python3 - <<EOF
import os; WORKSPACE = os.environ.get('WORKSPACE', os.getcwd())
import random
random.seed(42)

loaded_words = ["radical", "unprecedented", "allegedly", "controversial", "extreme", "biased", "sensational", "propaganda", "manipulative", "exaggerated"]
sources = ["Global News", "Daily Herald", "The Observer", "City Times", "Metro Report", "National Post", "The Sentinel", "World Gazette"]

base_texts = [
    "The government has introduced a new policy that has sparked a lot of debate among citizens.",
    "Experts claim the recent events have led to unprecedented changes in the economy.",
    "Critics argue that the measures are a radical departure from tradition.",
    "Some sources suggest the allegations are exaggerated and lack solid evidence.",
    "The controversial decision has divided public opinion sharply.",
    "Analysts warn about the extreme consequences of ignoring the warnings.",
    "Reports indicate a biased approach in the media coverage of the incident.",
    "The sensational headlines have drawn attention but may mislead readers.",
    "Observers note the propaganda efforts aimed at manipulating public perception.",
    "The manipulative tactics used by some parties have been widely criticized."
]

# Generate 25 articles
for i in range(25):
    source = random.choice(sources)
    # Compose article text with 5-10 sentences
    num_sentences = random.randint(5, 10)
    sentences = []
    for _ in range(num_sentences):
        sentence = random.choice(base_texts)
        # Randomly insert loaded words in some sentences
        if random.random() < 0.4:
            lw = random.choice(loaded_words)
            # Insert loaded word at random position in sentence
            words = sentence.split()
            pos = random.randint(0, len(words))
            words.insert(pos, lw)
            sentence = " ".join(words)
        sentences.append(sentence)
    article_text = " ".join(sentences)

    filename = f"article_{i+1:02d}.txt"
    with open(f"{WORKSPACE}/articles/{filename}", "w", encoding="utf-8") as f:
        f.write(f"Source: {source}\n")
        f.write(article_text + "\n")
EOF
