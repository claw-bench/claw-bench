#!/usr/bin/env bash
# Oracle solution for web-010-html-diff-report
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

python - "$WORKSPACE" << 'PYEOF'
import sys
import json
from html.parser import HTMLParser

ws = sys.argv[1]

class HTMLElement:
    def __init__(self, tag, attrs, parent=None):
        self.tag = tag
        self.attrs = dict(attrs) if attrs else {}
        self.id = self.attrs.get('id', '')
        self.cls = self.attrs.get('class', '')
        self.children = []
        self.text = ''
        self.parent = parent

    def key(self):
        if self.id:
            return ('id', self.tag, self.id)
        if self.cls:
            # Include parent id for disambiguation
            parent_id = ''
            if self.parent and self.parent.id:
                parent_id = self.parent.id
            elif self.parent and self.parent.parent and self.parent.parent.id:
                parent_id = self.parent.parent.id
            return ('cls', self.tag, self.cls, parent_id)
        return None

    def full_text(self):
        parts = [self.text]
        for ch in self.children:
            parts.append(ch.full_text())
        return ' '.join(p for p in parts if p).strip()

class SimpleHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.elements = []
        self.stack = []

    def handle_starttag(self, tag, attrs):
        parent = self.stack[-1] if self.stack else None
        el = HTMLElement(tag, attrs, parent)
        if parent:
            parent.children.append(el)
        self.elements.append(el)
        self.stack.append(el)

    def handle_endtag(self, tag):
        if self.stack and self.stack[-1].tag == tag:
            self.stack.pop()

    def handle_data(self, data):
        if self.stack and data.strip():
            self.stack[-1].text += data.strip()

def parse_html(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    parser = SimpleHTMLParser()
    parser.feed(content)
    return parser.elements

def build_element_map(elements):
    m = {}
    for el in elements:
        key = el.key()
        if key is None:
            continue
        if key not in m:
            m[key] = el
    return m

before_els = parse_html(f'{ws}/before.html')
after_els = parse_html(f'{ws}/after.html')

before_map = build_element_map(before_els)
after_map = build_element_map(after_els)

before_keys = set(before_map.keys())
after_keys = set(after_map.keys())

added = []
removed = []
modified = []

# Added elements
for key in sorted(after_keys - before_keys):
    el = after_map[key]
    desc = f"New {el.tag} element"
    ft = el.full_text()
    if ft:
        desc += f" containing '{ft[:60]}"
        if len(ft) > 60:
            desc += '...'
        desc += "'"
    added.append({
        'tag': el.tag,
        'id': el.id,
        'class': el.cls,
        'description': desc
    })

# Removed elements
for key in sorted(before_keys - after_keys):
    el = before_map[key]
    desc = f"Removed {el.tag} element"
    ft = el.full_text()
    if ft:
        desc += f" that contained '{ft[:60]}"
        if len(ft) > 60:
            desc += '...'
        desc += "'"
    removed.append({
        'tag': el.tag,
        'id': el.id,
        'class': el.cls,
        'description': desc
    })

# Modified elements
for key in sorted(before_keys & after_keys):
    bel = before_map[key]
    ael = after_map[key]
    changes = []

    bft = bel.full_text()
    aft = ael.full_text()
    if bft != aft and (bft.strip() or aft.strip()):
        changes.append(f"Text changed from '{bft[:50]}' to '{aft[:50]}'")
    if bel.cls != ael.cls:
        changes.append(f"Class changed from '{bel.cls}' to '{ael.cls}'")
    # Check other attribute changes
    all_attr_keys = set(bel.attrs.keys()) | set(ael.attrs.keys())
    for attr in sorted(all_attr_keys):
        if attr in ('id', 'class'):
            continue
        bval = bel.attrs.get(attr, '')
        aval = ael.attrs.get(attr, '')
        if bval != aval:
            changes.append(f"Attribute '{attr}' changed from '{bval}' to '{aval}'")

    if changes:
        modified.append({
            'tag': ael.tag,
            'id': ael.id,
            'class': ael.cls,
            'description': '; '.join(changes)
        })

report = {
    'added_elements': added,
    'removed_elements': removed,
    'modified_elements': modified
}

with open(f'{ws}/diff_report.json', 'w') as f:
    json.dump(report, f, indent=2)
    f.write('\n')
PYEOF

echo "Solution written to $WORKSPACE/diff_report.json"
