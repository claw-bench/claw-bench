#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${1:-workspace}"

python3 -c "
import re

with open('$WORKSPACE/document.md') as f:
    md = f.read()

# Simple markdown to HTML converter
lines = md.split('\n')
html_lines = []
in_code_block = False
in_ul = False
in_ol = False

def close_lists():
    r = []
    global in_ul, in_ol
    if in_ul:
        r.append('</ul>')
        in_ul = False
    if in_ol:
        r.append('</ol>')
        in_ol = False
    return r

def process_inline(text):
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # Italic
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    # Inline code
    text = re.sub(r'\x60(.+?)\x60', r'<code>\1</code>', text)
    # Links
    text = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href=\"\2\">\1</a>', text)
    return text

i = 0
while i < len(lines):
    line = lines[i]

    # Code block
    if line.strip().startswith('\x60\x60\x60'):
        if not in_code_block:
            html_lines.extend(close_lists())
            in_code_block = True
            html_lines.append('<pre><code>')
        else:
            in_code_block = False
            html_lines.append('</code></pre>')
        i += 1
        continue

    if in_code_block:
        html_lines.append(line)
        i += 1
        continue

    # Empty line
    if not line.strip():
        html_lines.extend(close_lists())
        i += 1
        continue

    # Headings
    m = re.match(r'^(#{1,6})\s+(.+)', line)
    if m:
        html_lines.extend(close_lists())
        level = len(m.group(1))
        text = process_inline(m.group(2))
        html_lines.append(f'<h{level}>{text}</h{level}>')
        i += 1
        continue

    # Unordered list
    m = re.match(r'^[-*]\s+(.+)', line)
    if m:
        if not in_ul:
            html_lines.extend(close_lists())
            html_lines.append('<ul>')
            in_ul = True
        html_lines.append(f'<li>{process_inline(m.group(1))}</li>')
        i += 1
        continue

    # Ordered list
    m = re.match(r'^\d+\.\s+(.+)', line)
    if m:
        if not in_ol:
            html_lines.extend(close_lists())
            html_lines.append('<ol>')
            in_ol = True
        html_lines.append(f'<li>{process_inline(m.group(1))}</li>')
        i += 1
        continue

    # Paragraph
    html_lines.extend(close_lists())
    html_lines.append(f'<p>{process_inline(line)}</p>')
    i += 1

html_lines.extend(close_lists())

with open('$WORKSPACE/output.html', 'w') as f:
    f.write('\n'.join(html_lines) + '\n')
"

echo "Solution written to $WORKSPACE/output.html"
