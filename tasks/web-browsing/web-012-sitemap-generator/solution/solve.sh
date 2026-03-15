#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

python - "$WORKSPACE" << 'PYEOF'
import sys
import json
import os
import re

ws = sys.argv[1]
pages_dir = f"{ws}/pages"

# Get list of all HTML files
html_files = sorted([f for f in os.listdir(pages_dir) if f.endswith(".html")])
html_set = set(html_files)

sitemap = {}
for filename in html_files:
    with open(f"{pages_dir}/{filename}", "r") as f:
        html = f.read()
    # Find all href values
    hrefs = re.findall(r'<a\s+[^>]*href="([^"]*)"', html)
    # Filter to only internal page links
    links = sorted(set(h for h in hrefs if h in html_set))
    sitemap[filename] = links

with open(f"{ws}/sitemap.json", "w") as f:
    json.dump(sitemap, f, indent=2)
PYEOF
