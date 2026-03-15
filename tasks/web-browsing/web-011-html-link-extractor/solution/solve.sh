#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

python - "$WORKSPACE" << 'PYEOF'
import sys
import json
import re

ws = sys.argv[1]

with open(f"{ws}/page.html", "r") as f:
    html = f.read()

# Find all <a> tags with href
pattern = r'<a\s+[^>]*href="([^"]*)"[^>]*>(.*?)</a>'
matches = re.findall(pattern, html, re.DOTALL)

links = []
for url, text in matches:
    text = text.strip()
    if url.startswith("#"):
        link_type = "anchor"
    elif "://" in url:
        link_type = "external"
    else:
        link_type = "internal"
    links.append({"url": url, "text": text, "type": link_type})

with open(f"{ws}/links.json", "w") as f:
    json.dump(links, f, indent=2)
PYEOF
