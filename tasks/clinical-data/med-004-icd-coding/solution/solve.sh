#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

python3 - <<EOF
import os
import csv
import json
import re

notes_dir = os.path.join(os.environ.get('WORKSPACE', 'workspace'), 'clinical_notes')
icd_map_file = os.path.join(os.environ.get('WORKSPACE', 'workspace'), 'icd_mapping.csv')
output_file = os.path.join(os.environ.get('WORKSPACE', 'workspace'), 'coded_records.json')

# Load ICD mapping
keyword_to_code = {}
with open(icd_map_file, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        keyword = row['keyword'].lower()
        icd_code = row['icd_code']
        keyword_to_code[keyword] = icd_code

# Precompile regex patterns for keywords for whole word matching
# Use word boundaries and escape keywords
keyword_patterns = {}
for kw in keyword_to_code.keys():
    # Replace spaces with \s+ to match any whitespace
    pattern_str = r'\\b' + re.sub(r'\\s+', r'\\\s+', re.escape(kw)) + r'\\b'
    keyword_patterns[kw] = re.compile(pattern_str, re.IGNORECASE)

coded_records = {}

for filename in sorted(os.listdir(notes_dir)):
    if not filename.endswith('.txt'):
        continue
    filepath = os.path.join(notes_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    matched_codes = set()
    for kw, pattern in keyword_patterns.items():
        if pattern.search(text):
            matched_codes.add(keyword_to_code[kw])

    coded_records[filename] = sorted(matched_codes)

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(coded_records, f, indent=2)
EOF
