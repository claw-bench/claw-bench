#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${1:-workspace}"

python3 -c "
import re, glob, json

chapters = sorted(glob.glob('$WORKSPACE/chapters/chapter-*.md'))

book_lines = ['# Complete Guide', '', '## Table of Contents', '']

# First pass: collect TOC entries
toc_entries = []
for idx, ch_path in enumerate(chapters, 1):
    with open(ch_path) as f:
        for line in f:
            m = re.match(r'^(#{1,6})\s+(.+)', line.strip())
            if m:
                level = len(m.group(1))
                title = m.group(2)
                if level == 1:
                    toc_entries.append(f'{idx}. {title}')
                elif level == 2:
                    toc_entries.append(f'   {idx}.{len([e for e in toc_entries if e.startswith(\"   \") and toc_entries.index(e) > [i for i,x in enumerate(toc_entries) if not x.startswith(\" \")][-1]]) + 1} {title}')

# Simpler TOC: just list chapters and subsections
book_lines = ['# Complete Guide', '', '## Table of Contents', '']
sub_counter = 0
ch_num = 0
for idx, ch_path in enumerate(chapters, 1):
    with open(ch_path) as f:
        lines = f.readlines()
    sub_counter = 0
    for line in lines:
        m = re.match(r'^(#{1,6})\s+(.+)', line.strip())
        if m:
            level = len(m.group(1))
            title = m.group(2)
            if level == 1:
                ch_num = idx
                book_lines.append(f'{idx}. {title}')
            elif level == 2:
                sub_counter += 1
                book_lines.append(f'   {ch_num}.{sub_counter} {title}')

book_lines.append('')

# Second pass: merge content
for idx, ch_path in enumerate(chapters):
    if idx > 0:
        book_lines.append('---')
        book_lines.append('')
    with open(ch_path) as f:
        content = f.read().strip()
    # Adjust heading levels: # -> ##, ## -> ###, etc.
    adjusted = []
    for line in content.split('\n'):
        m = re.match(r'^(#{1,6})\s+(.+)', line)
        if m:
            new_level = len(m.group(1)) + 1
            adjusted.append('#' * new_level + ' ' + m.group(2))
        else:
            adjusted.append(line)
    book_lines.extend(adjusted)
    book_lines.append('')

with open('$WORKSPACE/book.md', 'w') as f:
    f.write('\n'.join(book_lines))
"

echo "Solution written to $WORKSPACE/book.md"
