#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${1:-workspace}"

python3 -c "
import json, re, glob, os
from collections import Counter

pages = []
all_issues = []

for fpath in sorted(glob.glob('$WORKSPACE/site/*.html')):
    fname = os.path.basename(fpath)
    with open(fpath) as f:
        html = f.read()

    issues = []

    # Title
    title_m = re.search(r'<title>(.*?)</title>', html)
    title = title_m.group(1) if title_m else ''
    if len(title) < 30:
        issues.append('title_too_short')

    # Meta description
    has_meta = bool(re.search(r'<meta\s+name=\"description\"', html))
    if not has_meta:
        issues.append('missing_meta_description')

    # Viewport
    has_viewport = bool(re.search(r'<meta\s+name=\"viewport\"', html))
    if not has_viewport:
        issues.append('missing_viewport')

    # Canonical
    has_canonical = bool(re.search(r'<link\s+rel=\"canonical\"', html))
    if not has_canonical:
        issues.append('missing_canonical')

    # H1 count
    h1s = re.findall(r'<h1[^>]*>', html)
    h1_count = len(h1s)
    if h1_count == 0:
        issues.append('missing_h1')
    elif h1_count > 1:
        issues.append('multiple_h1')

    # Missing alt
    for m in re.finditer(r'<img\s+([^>]+)>', html):
        if 'alt=' not in m.group(1):
            issues.append('missing_alt')

    # Empty links
    for m in re.finditer(r'<a\s+[^>]*href=\"([^\"]*)\"[^>]*>', html):
        if not m.group(1).strip():
            issues.append('empty_link')

    # Heading skip
    headings = [int(h) for h in re.findall(r'<h(\d)', html)]
    for i in range(1, len(headings)):
        if headings[i] > headings[i-1] + 1:
            issues.append('heading_skip')
            break

    all_issues.extend(issues)
    pages.append({
        'file': fname,
        'title': title,
        'has_meta_description': has_meta,
        'has_viewport': has_viewport,
        'has_canonical': has_canonical,
        'h1_count': h1_count,
        'issues': issues
    })

result = {
    'pages': pages,
    'total_issues': len(all_issues),
    'issue_summary': dict(Counter(all_issues))
}

with open('$WORKSPACE/seo_report.json', 'w') as f:
    json.dump(result, f, indent=2)
"

echo "Solution written to $WORKSPACE/seo_report.json"
