#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

PAPERS_DIR="$WORKSPACE/papers"
BIB_CSV="$WORKSPACE/bibliography.csv"
META_JSON="$WORKSPACE/metadata.json"

# Use python3 inline script to parse and write outputs
python3 - <<'EOF'
import os
import json
import csv

papers_dir = os.path.join(os.environ['WORKSPACE'], 'papers')

filenames = sorted(f for f in os.listdir(papers_dir) if f.endswith('.txt'))

metadata_list = []

for fname in filenames:
    path = os.path.join(papers_dir, fname)
    with open(path, 'r', encoding='utf-8') as f:
        lines = [line.rstrip('\n') for line in f]

    # Parse fields
    title = None
    authors = None
    year = None
    keywords = None
    abstract_lines = []
    references = []

    # States: None, 'abstract', 'references'
    state = None

    for i, line in enumerate(lines):
        if line.startswith('Title:'):
            title = line[len('Title:'):].strip()
            state = None
        elif line.startswith('Authors:'):
            authors = [a.strip() for a in line[len('Authors:'):].split(';')]
            state = None
        elif line.startswith('Year:'):
            year_str = line[len('Year:'):].strip()
            year = int(year_str)
            state = None
        elif line.startswith('Keywords:'):
            keywords = [k.strip() for k in line[len('Keywords:'):].split(';')]
            state = None
        elif line == 'Abstract:':
            state = 'abstract'
        elif line == 'References:':
            state = 'references'
        elif line.strip() == '':
            # blank line resets state except if in abstract or references
            if state in ('abstract', 'references'):
                # blank lines inside abstract or references are allowed, keep state
                pass
            else:
                state = None
        else:
            if state == 'abstract':
                abstract_lines.append(line)
            elif state == 'references':
                references.append(line)

    abstract = '\n'.join(abstract_lines).strip()

    metadata = {
        'title': title,
        'authors': authors,
        'year': year,
        'keywords': keywords,
        'abstract': abstract,
        'references': references
    }

    metadata_list.append(metadata)

# Write bibliography.csv
with open(os.path.join(os.environ['WORKSPACE'], 'bibliography.csv'), 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['title', 'authors', 'year', 'keywords'])
    writer.writeheader()
    for m in metadata_list:
        writer.writerow({
            'title': m['title'],
            'authors': '; '.join(m['authors']),
            'year': str(m['year']),
            'keywords': '; '.join(m['keywords'])
        })

# Write metadata.json
with open(os.path.join(os.environ['WORKSPACE'], 'metadata.json'), 'w', encoding='utf-8') as f:
    json.dump(metadata_list, f, indent=2, ensure_ascii=False)
EOF
