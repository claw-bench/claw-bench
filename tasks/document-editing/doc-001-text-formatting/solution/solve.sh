#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${1:-workspace}"

python3 -c "
import re, json, textwrap

with open('$WORKSPACE/rules.json') as f:
    rules = json.load(f)

with open('$WORKSPACE/document.txt') as f:
    text = f.read()

max_len = rules['max_line_length']
result_lines = []

for paragraph in text.split('\n'):
    if not paragraph.strip():
        result_lines.append('')
        continue

    # Check indentation
    indent = ''
    if paragraph.startswith('  ') and not paragraph.startswith('   '):
        indent = '  '
        paragraph = paragraph[2:]

    # Normalize whitespace
    line = re.sub(r'[ \t]+', ' ', paragraph).strip()

    # Fix punctuation: remove space before punctuation
    line = re.sub(r'\s+([.,;:])', r'\1', line)
    # Ensure space after punctuation (if not end of string)
    line = re.sub(r'([.,;:])([^\s])', r'\1 \2', line)

    # Wrap
    if indent:
        wrapped = textwrap.fill(line, width=max_len - len(indent))
        for wl in wrapped.split('\n'):
            result_lines.append(indent + wl)
    else:
        wrapped = textwrap.fill(line, width=max_len)
        result_lines.extend(wrapped.split('\n'))

with open('$WORKSPACE/formatted.txt', 'w') as f:
    f.write('\n'.join(result_lines) + '\n')
"

echo "Solution written to $WORKSPACE/formatted.txt"
