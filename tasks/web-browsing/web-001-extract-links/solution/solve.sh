#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${1:-workspace}"

python3 -c "
import json, re

with open('$WORKSPACE/page.html') as f:
    html = f.read()

links = []
for m in re.finditer(r'<a\s+[^>]*href=\"([^\"]+)\"[^>]*>(.*?)</a>', html, re.DOTALL):
    url = m.group(1)
    text = re.sub(r'<[^>]+>', '', m.group(2)).strip()
    if url.startswith('/') or 'example.com' in url:
        link_type = 'internal'
    else:
        link_type = 'external'
    links.append({'url': url, 'text': text, 'type': link_type})

internal = sum(1 for l in links if l['type'] == 'internal')
external = sum(1 for l in links if l['type'] == 'external')

result = {
    'links': links,
    'total_count': len(links),
    'internal_count': internal,
    'external_count': external
}

with open('$WORKSPACE/links.json', 'w') as f:
    json.dump(result, f, indent=2)
"

echo "Solution written to $WORKSPACE/links.json"
