#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${1:-workspace}"

python3 -c "
import json, re, glob, os

site_dir = '$WORKSPACE/site'
files = sorted(glob.glob(f'{site_dir}/*.html'))

# Build map of existing paths
path_to_file = {}
file_to_path = {}
for fpath in files:
    fname = os.path.basename(fpath)
    if fname == 'index.html':
        path = '/'
    else:
        path = '/' + fname.replace('.html', '')
    path_to_file[path] = fname
    file_to_path[fname] = path

existing_paths = set(path_to_file.keys())

# Parse each page
pages = []
all_links = {}
broken = []
total_internal = 0

for fpath in files:
    fname = os.path.basename(fpath)
    with open(fpath) as f:
        html = f.read()

    title_m = re.search(r'<title>(.*?)</title>', html)
    title = title_m.group(1) if title_m else ''

    page_path = file_to_path[fname]
    links_to = []

    for m in re.finditer(r'href=\"([^\"]+)\"', html):
        href = m.group(1)
        if href.startswith('/'):
            links_to.append(href)
            total_internal += 1
            if href not in existing_paths:
                broken.append({
                    'source_file': fname,
                    'link_href': href,
                    'reason': 'Target page does not exist in site'
                })

    all_links[fname] = links_to
    pages.append({
        'file': fname,
        'title': title,
        'path': page_path,
        'links_to': links_to,
        'linked_from': []
    })

# Build linked_from
for page in pages:
    for other_page in pages:
        if page['path'] in other_page['links_to']:
            page['linked_from'].append(other_page['path'])

sitemap = {
    'pages': pages,
    'total_pages': len(pages),
    'total_internal_links': total_internal
}

broken_links = {
    'broken': broken,
    'total_broken': len(broken)
}

with open('$WORKSPACE/sitemap.json', 'w') as f:
    json.dump(sitemap, f, indent=2)
with open('$WORKSPACE/broken_links.json', 'w') as f:
    json.dump(broken_links, f, indent=2)
"

echo "Solution written to $WORKSPACE/"
