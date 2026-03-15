#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${1:-workspace}"

python3 -c "
import json, re, glob, os
from collections import Counter

issues = []
files = sorted(glob.glob('$WORKSPACE/site/*.html'))

for fpath in files:
    fname = os.path.basename(fpath)
    with open(fpath) as f:
        html = f.read()

    # missing_alt: img without alt attribute
    for m in re.finditer(r'<img\s+([^>]+)>', html):
        attrs = m.group(1)
        if 'alt=' not in attrs:
            issues.append({'file': fname, 'category': 'missing_alt', 'element': m.group(0)[:80], 'description': 'Image missing alt attribute'})

    # missing_label: inputs without associated label
    label_fors = set(re.findall(r'<label\s+for=\"(\w+)\"', html))
    for m in re.finditer(r'<(input|select|textarea)\s+([^>]+)>', html):
        tag = m.group(1)
        attrs = m.group(2)
        type_m = re.search(r'type=\"(\w+)\"', attrs)
        if type_m and type_m.group(1) in ('submit', 'button', 'hidden'):
            continue
        id_m = re.search(r'id=\"(\w+)\"', attrs)
        field_id = id_m.group(1) if id_m else None
        if not field_id or field_id not in label_fors:
            issues.append({'file': fname, 'category': 'missing_label', 'element': m.group(0)[:80], 'description': f'{tag} element without associated label'})

    # empty_link
    for m in re.finditer(r'<a\s+[^>]*>(.*?)</a>', html, re.DOTALL):
        text = re.sub(r'<[^>]+>', '', m.group(1)).strip()
        if not text:
            issues.append({'file': fname, 'category': 'empty_link', 'element': m.group(0)[:80], 'description': 'Link with no text content'})

    # missing_lang
    html_tag = re.search(r'<html([^>]*)>', html)
    if html_tag and 'lang=' not in html_tag.group(1):
        issues.append({'file': fname, 'category': 'missing_lang', 'element': '<html>', 'description': 'HTML element missing lang attribute'})

    # skipped_heading
    headings = re.findall(r'<h(\d)', html)
    for i in range(1, len(headings)):
        prev = int(headings[i-1])
        curr = int(headings[i])
        if curr > prev + 1:
            issues.append({'file': fname, 'category': 'skipped_heading', 'element': f'h{prev} -> h{curr}', 'description': f'Heading level skipped from h{prev} to h{curr}'})

    # missing_table_header
    if '<table>' in html or '<table ' in html:
        if '<th>' not in html and '<th ' not in html:
            issues.append({'file': fname, 'category': 'missing_table_header', 'element': '<table>', 'description': 'Table without header cells'})

    # no_alt_video
    for m in re.finditer(r'<video\s+([^>]+)>(.*?)</video>', html, re.DOTALL):
        if '<track' not in m.group(2):
            issues.append({'file': fname, 'category': 'no_alt_video', 'element': m.group(0)[:80], 'description': 'Video without text track'})
    for m in re.finditer(r'<video\s+([^>]+)/?\s*>', html):
        issues.append({'file': fname, 'category': 'no_alt_video', 'element': m.group(0)[:80], 'description': 'Video without text track'})

    # clickable_div
    for m in re.finditer(r'<div\s+([^>]*onclick[^>]*)>', html):
        attrs = m.group(1)
        if 'role=' not in attrs and 'tabindex=' not in attrs:
            issues.append({'file': fname, 'category': 'clickable_div', 'element': m.group(0)[:80], 'description': 'Clickable div without role or tabindex'})

summary = dict(Counter(i['category'] for i in issues))

result = {
    'issues': issues,
    'summary': summary,
    'files_scanned': len(files),
    'total_issues': len(issues)
}

with open('$WORKSPACE/accessibility_report.json', 'w') as f:
    json.dump(result, f, indent=2)
"

echo "Solution written to $WORKSPACE/accessibility_report.json"
