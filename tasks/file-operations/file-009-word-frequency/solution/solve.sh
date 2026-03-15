#!/usr/bin/env bash
# Oracle solution for file-009-word-frequency
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

python3 -c "
import re
from collections import Counter

with open('$WORKSPACE/article.txt') as f:
    text = f.read().lower()

# Strip punctuation
text = re.sub(r'[.,;:!?()\"\'\\-]', ' ', text)
words = text.split()

counts = Counter(words)
# Sort by count descending, then alphabetically ascending
sorted_words = sorted(counts.items(), key=lambda x: (-x[1], x[0]))

with open('$WORKSPACE/frequencies.csv', 'w') as f:
    f.write('word,count\n')
    for word, count in sorted_words:
        f.write(f'{word},{count}\n')
"

echo "Solution written to $WORKSPACE/frequencies.csv"
