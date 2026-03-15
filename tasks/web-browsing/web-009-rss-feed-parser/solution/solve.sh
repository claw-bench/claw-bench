#!/usr/bin/env bash
# Oracle solution for web-009-rss-feed-parser
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

python - "$WORKSPACE" << 'PYEOF'
import sys
import json
import re
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

ws = sys.argv[1]

def strip_html(text):
    """Remove HTML tags from text."""
    clean = re.sub(r'<[^>]+>', '', text)
    # Collapse whitespace
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean

tree = ET.parse(f'{ws}/feed.xml')
root = tree.getroot()

items = []
for item_el in root.iter('item'):
    title = item_el.find('title').text or ''
    link = item_el.find('link').text or ''
    pub_date = item_el.find('pubDate').text or ''
    desc_el = item_el.find('description')
    description = strip_html(desc_el.text or '') if desc_el is not None else ''

    items.append({
        'title': title.strip(),
        'link': link.strip(),
        'pubDate': pub_date.strip(),
        'description': description,
    })

# Sort by date descending
def parse_date(item):
    try:
        return parsedate_to_datetime(item['pubDate'])
    except Exception:
        from datetime import datetime
        return datetime.min

items.sort(key=parse_date, reverse=True)

with open(f'{ws}/feed_items.json', 'w') as f:
    json.dump(items, f, indent=2)
    f.write('\n')
PYEOF

echo "Solution written to $WORKSPACE/feed_items.json"
