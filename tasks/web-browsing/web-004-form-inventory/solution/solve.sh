#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${1:-workspace}"

python3 -c "
import json, re

with open('$WORKSPACE/form.html') as f:
    html = f.read()

# Extract labels
labels = {}
for m in re.finditer(r'<label\s+for=\"(\w+)\">(.*?)</label>', html):
    labels[m.group(1)] = m.group(2).strip()

fields = []

# Input fields
for m in re.finditer(r'<input\s+([^>]+)>', html):
    attrs_str = m.group(1)
    attrs = dict(re.findall(r'(\w+)=\"([^\"]+)\"', attrs_str))
    field_id = attrs.get('id', '')
    field_type = attrs.get('type', 'text')
    validation = {}
    for v in ['minlength', 'maxlength', 'pattern', 'min', 'max']:
        if v in attrs:
            validation[v] = attrs[v]
    fields.append({
        'name': attrs.get('name', ''),
        'type': field_type,
        'required': 'required' in attrs_str and '=\"' not in attrs_str.split('required')[0].split()[-1] if 'required' in attrs_str else False,
        'label': labels.get(field_id, ''),
        'validation': validation
    })
    # Fix required detection
    fields[-1]['required'] = bool(re.search(r'\brequired\b', attrs_str))

# Select fields
for m in re.finditer(r'<select\s+([^>]+)>', html):
    attrs_str = m.group(1)
    attrs = dict(re.findall(r'(\w+)=\"([^\"]+)\"', attrs_str))
    field_id = attrs.get('id', '')
    fields.append({
        'name': attrs.get('name', ''),
        'type': 'select',
        'required': bool(re.search(r'\brequired\b', attrs_str)),
        'label': labels.get(field_id, ''),
        'validation': {}
    })

# Textarea fields
for m in re.finditer(r'<textarea\s+([^>]+)>', html):
    attrs_str = m.group(1)
    attrs = dict(re.findall(r'(\w+)=\"([^\"]+)\"', attrs_str))
    field_id = attrs.get('id', '')
    validation = {}
    for v in ['minlength', 'maxlength']:
        if v in attrs:
            validation[v] = attrs[v]
    fields.append({
        'name': attrs.get('name', ''),
        'type': 'textarea',
        'required': bool(re.search(r'\brequired\b', attrs_str)),
        'label': labels.get(field_id, ''),
        'validation': validation
    })

with open('$WORKSPACE/form_fields.json', 'w') as f:
    json.dump(fields, f, indent=2)
"

echo "Solution written to $WORKSPACE/form_fields.json"
