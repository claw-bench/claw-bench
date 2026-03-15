#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
mkdir -p "$WORKSPACE"

python - "$WORKSPACE" << 'PYEOF'
import xml.etree.ElementTree as ET
import json
import sys

ws = sys.argv[1]

def parse_element(elem):
    result = {}

    # Handle attributes
    if elem.attrib:
        result['@attributes'] = dict(elem.attrib)

    children = list(elem)
    if not children:
        # Leaf element: text only
        text = (elem.text or '').strip()
        if elem.attrib:
            result['#text'] = text
            return result
        else:
            return text

    # Group children by tag
    tag_counts = {}
    for child in children:
        tag_counts[child.tag] = tag_counts.get(child.tag, 0) + 1

    for child in children:
        parsed = parse_element(child)
        tag = child.tag
        if tag_counts[tag] > 1:
            if tag not in result:
                result[tag] = []
            result[tag].append(parsed)
        else:
            result[tag] = parsed

    return result

tree = ET.parse(f'{ws}/config.xml')
root = tree.getroot()

output = {root.tag: parse_element(root)}

with open(f'{ws}/config.json', 'w') as f:
    json.dump(output, f, indent=2)
PYEOF

echo "Solution written to $WORKSPACE/config.json"
