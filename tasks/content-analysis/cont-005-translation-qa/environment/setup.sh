#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

mkdir -p "$WORKSPACE/source"
mkdir -p "$WORKSPACE/translation"

python3 - <<'EOF'
import random
import os

random.seed(42)

source_dir = os.path.join(os.environ['WORKSPACE'], 'source')
translation_dir = os.path.join(os.environ['WORKSPACE'], 'translation')

# Some sample sentences to generate source lines
sample_sentences = [
    "The quick brown fox jumps over the lazy dog.",
    "This is a test sentence for translation.",
    "Artificial intelligence is transforming many industries.",
    "Machine learning enables computers to learn from data.",
    "Natural language processing is a complex field.",
    "Python is a popular programming language.",
    "Data science involves statistics and programming.",
    "Deep learning uses neural networks.",
    "Evaluation metrics are important for quality assessment.",
    "Open source software fosters collaboration.",
    "Cloud computing provides scalable resources.",
    "Big data analytics uncovers hidden patterns.",
    "Robotics integrates hardware and software.",
    "Computer vision allows machines to see.",
    "Autonomous vehicles rely on sensors.",
    "Speech recognition converts audio to text.",
    "Translation requires understanding context.",
    "Quality assurance ensures product reliability.",
    "User experience design improves usability.",
    "Cybersecurity protects information systems."
]

num_files = 25
min_lines = 15
max_lines = 25

for i in range(1, num_files + 1):
    filename = f'doc_{i:02d}.txt'
    num_lines = random.randint(min_lines, max_lines)
    # Generate source lines
    source_lines = random.choices(sample_sentences, k=num_lines)

    # Write source file
    with open(os.path.join(source_dir, filename), 'w', encoding='utf-8') as f:
        for line in source_lines:
            f.write(line + '\n')

    # Generate translation lines
    translation_lines = []
    for line in source_lines:
        # With 80% chance, keep line (possibly modified)
        if random.random() < 0.8:
            # Slightly modify line by shuffling words or replacing some words
            words = line.split()
            if len(words) > 3 and random.random() < 0.3:
                # shuffle words (except first and last)
                middle = words[1:-1]
                random.shuffle(middle)
                words = [words[0]] + middle + [words[-1]]
            elif random.random() < 0.3:
                # replace a word randomly
                idx = random.randint(0, len(words)-1)
                replacement = random.choice(["AI", "ML", "data", "system", "model", "network"])
                words[idx] = replacement
            translation_lines.append(' '.join(words))
        else:
            # missing segment: skip this line
            pass

    # Add some extra lines (added segments) with 10% chance per line
    for _ in range(random.randint(0, 3)):
        extra_line = random.choice(sample_sentences)
        translation_lines.insert(random.randint(0, len(translation_lines)), extra_line)

    # Write translation file
    with open(os.path.join(translation_dir, filename), 'w', encoding='utf-8') as f:
        for line in translation_lines:
            f.write(line + '\n')
EOF
