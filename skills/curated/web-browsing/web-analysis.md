# Web Analysis Skill

## Overview
This skill provides guidance on web content analysis including HTML parsing,
accessibility auditing, SEO analysis, and structured data extraction.

## HTML Parsing

### Link Extraction
```python
from html.parser import HTMLParser
from urllib.parse import urljoin

class LinkExtractor(HTMLParser):
    def __init__(self, base_url=""):
        super().__init__()
        self.base_url = base_url
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for name, value in attrs:
                if name == "href" and value:
                    url = urljoin(self.base_url, value)
                    self.links.append(url)

def extract_links(html, base_url=""):
    parser = LinkExtractor(base_url)
    parser.feed(html)
    return parser.links
```

### Table Extraction
```python
import re

def extract_tables(html):
    """Extract tables from HTML into lists of row dictionaries."""
    tables = []
    table_pattern = re.compile(r"<table[^>]*>(.*?)</table>", re.DOTALL)
    row_pattern = re.compile(r"<tr[^>]*>(.*?)</tr>", re.DOTALL)
    cell_pattern = re.compile(r"<t[dh][^>]*>(.*?)</t[dh]>", re.DOTALL)

    for table_match in table_pattern.finditer(html):
        rows = []
        for row_match in row_pattern.finditer(table_match.group(1)):
            cells = [
                re.sub(r"<[^>]+>", "", c.group(1)).strip()
                for c in cell_pattern.finditer(row_match.group(1))
            ]
            rows.append(cells)
        if rows:
            # Use first row as headers if it contains <th>
            headers = rows[0]
            data = [dict(zip(headers, row)) for row in rows[1:]]
            tables.append({"headers": headers, "rows": data})
    return tables
```

### Form Analysis
Identify form elements and their structure:
- Extract `<form>` elements with their action URLs and methods.
- List all `<input>`, `<select>`, and `<textarea>` fields.
- Note required fields, input types, and validation attributes.
- Map field names to their labels for usability analysis.

```python
def extract_form_fields(html):
    """Extract form fields and their attributes."""
    fields = []
    input_pattern = re.compile(
        r'<input\s+([^>]*)>', re.DOTALL | re.IGNORECASE
    )
    for match in input_pattern.finditer(html):
        attrs = parse_attributes(match.group(1))
        fields.append({
            "type": attrs.get("type", "text"),
            "name": attrs.get("name", ""),
            "required": "required" in attrs,
            "value": attrs.get("value", ""),
        })
    return fields

def parse_attributes(attr_string):
    """Parse HTML attributes into a dictionary."""
    attrs = {}
    for match in re.finditer(r'(\w+)\s*=\s*["\']([^"\']*)["\']', attr_string):
        attrs[match.group(1)] = match.group(2)
    # Handle boolean attributes (no value)
    for match in re.finditer(r'\b(\w+)(?=\s|$)(?!=)', attr_string):
        if match.group(1) not in attrs:
            attrs[match.group(1)] = match.group(1)
    return attrs
```

## Accessibility Auditing (WCAG)

### Image Accessibility
- Every `<img>` must have an `alt` attribute.
- Decorative images should use `alt=""` (empty but present).
- Complex images (charts, diagrams) need detailed descriptions.

```python
def check_image_alt(html):
    """Find images missing alt text."""
    issues = []
    img_pattern = re.compile(r"<img\s+([^>]*)>", re.IGNORECASE)
    for match in img_pattern.finditer(html):
        attrs = parse_attributes(match.group(1))
        if "alt" not in attrs:
            src = attrs.get("src", "unknown")
            issues.append(f"Missing alt text: {src}")
    return issues
```

### Heading Hierarchy
- Headings must not skip levels (h1 -> h3 without h2 is invalid).
- There should be exactly one `<h1>` per page.
- Headings should create a logical document outline.

```python
def check_heading_hierarchy(html):
    """Verify heading levels follow proper hierarchy."""
    heading_pattern = re.compile(r"<h(\d)[^>]*>", re.IGNORECASE)
    levels = [int(m.group(1)) for m in heading_pattern.finditer(html)]
    issues = []

    if levels and levels[0] != 1:
        issues.append("First heading is not h1")
    if levels.count(1) > 1:
        issues.append(f"Multiple h1 elements found: {levels.count(1)}")

    for i in range(1, len(levels)):
        if levels[i] > levels[i - 1] + 1:
            issues.append(f"Heading skip: h{levels[i-1]} to h{levels[i]}")
    return issues
```

### Additional WCAG Checks
- **Color contrast**: Text must have sufficient contrast ratio (4.5:1 for normal, 3:1 for large).
- **Form labels**: Every input must have an associated `<label>`.
- **Keyboard navigation**: Interactive elements must be focusable and operable via keyboard.
- **Language attribute**: `<html>` should have a `lang` attribute.
- **Link text**: Avoid generic "click here"; links should be descriptive.

## SEO Analysis

### Meta Tag Audit
```python
def extract_meta_tags(html):
    """Extract meta tags relevant to SEO."""
    meta = {}
    title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.DOTALL)
    if title_match:
        meta["title"] = title_match.group(1).strip()

    meta_pattern = re.compile(
        r'<meta\s+(?:name|property)\s*=\s*["\']([^"\']+)["\']\s+'
        r'content\s*=\s*["\']([^"\']*)["\']', re.IGNORECASE
    )
    for match in meta_pattern.finditer(html):
        meta[match.group(1)] = match.group(2)
    return meta
```

### SEO Checklist
- **Title tag**: Present, unique, 50-60 characters.
- **Meta description**: Present, 150-160 characters, includes target keywords.
- **Canonical URL**: `<link rel="canonical">` prevents duplicate content issues.
- **Open Graph tags**: og:title, og:description, og:image for social sharing.
- **Heading structure**: Logical h1-h6 hierarchy with keywords in h1.
- **Image optimization**: Alt text present, reasonable file sizes.
- **Internal linking**: Pages should link to related content.

## Structured Data Extraction

### JSON-LD Extraction
```python
import json

def extract_jsonld(html):
    """Extract JSON-LD structured data from a page."""
    pattern = re.compile(
        r'<script\s+type\s*=\s*["\']application/ld\+json["\']\s*>(.*?)</script>',
        re.DOTALL | re.IGNORECASE
    )
    results = []
    for match in pattern.finditer(html):
        try:
            data = json.loads(match.group(1))
            results.append(data)
        except json.JSONDecodeError:
            pass
    return results
```

## Best Practices
- Use a proper HTML parser (html.parser, BeautifulSoup, lxml) instead of regex
  for production-grade work; regex examples here illustrate the logic.
- Always resolve relative URLs against the page's base URL.
- Handle character encoding declared in meta tags or HTTP headers.
- Rate-limit requests when crawling multiple pages and respect robots.txt.
