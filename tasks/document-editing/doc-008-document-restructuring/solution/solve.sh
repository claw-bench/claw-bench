#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${1:-workspace}"

python3 -c "
import json, re

with open('$WORKSPACE/messy_doc.md') as f:
    doc = f.read()
with open('$WORKSPACE/outline.json') as f:
    outline = json.load(f)

# Parse sections from the messy doc
sections = {}
current_section = None
current_content = []
in_code_block = False

for line in doc.split('\n'):
    if line.startswith('\`\`\`'):
        in_code_block = not in_code_block
        current_content.append(line)
        continue
    m = re.match(r'^#{1,4}\s+(.+)', line)
    if m and not in_code_block:
        if current_section is not None:
            sections[current_section] = '\n'.join(current_content).strip()
        current_section = m.group(1).strip()
        current_content = []
    else:
        current_content.append(line)

if current_section:
    sections[current_section] = '\n'.join(current_content).strip()

# Build structured doc
output = [f'# {outline[\"title\"]}', '']

for section in outline['sections']:
    output.append(f'## {section[\"title\"]}')
    output.append('')
    # Add section content if it exists
    if section['title'] in sections and sections[section['title']]:
        output.append(sections[section['title']])
        output.append('')
    for sub in section.get('subsections', []):
        output.append(f'### {sub}')
        output.append('')
        if sub in sections and sections[sub]:
            output.append(sections[sub])
            output.append('')
        # Check for sub-subsections (e.g., List Users, Create User under Users)
        if sub == 'Users':
            for key in ['List Users', 'Create User', 'Get User']:
                if key in sections:
                    output.append(f'#### {key}')
                    output.append('')
                    output.append(sections[key])
                    output.append('')
        elif sub == 'Orders':
            for key in ['List Orders', 'Create Order', 'Get Order']:
                if key in sections:
                    output.append(f'#### {key}')
                    output.append('')
                    output.append(sections[key])
                    output.append('')

with open('$WORKSPACE/structured_doc.md', 'w') as f:
    f.write('\n'.join(output))
"

echo "Solution written to $WORKSPACE/structured_doc.md"
