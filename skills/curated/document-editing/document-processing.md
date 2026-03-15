# Document Processing Skill

## Overview
This skill provides guidance on document handling including text formatting,
Markdown/HTML conversion, template rendering, document comparison, and TOC generation.

## Text Formatting Rules

### Whitespace Normalization
- Collapse multiple spaces into a single space.
- Normalize line endings to `\n` (from `\r\n` or `\r`).
- Trim trailing whitespace from each line.
- Ensure the file ends with exactly one newline.

```python
import re

def normalize_whitespace(text):
    """Clean up inconsistent whitespace in text."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = text.split("\n")
    lines = [line.rstrip() for line in lines]
    text = "\n".join(lines)
    text = text.strip() + "\n"
    return text
```

### Consistent Indentation
- Detect whether the document uses tabs or spaces.
- Convert to the target style consistently.
- Preserve relative indentation levels.

```python
def convert_indent(text, from_char="\t", to_chars="    "):
    """Convert indentation style."""
    lines = text.split("\n")
    result = []
    for line in lines:
        stripped = line.lstrip(from_char)
        indent_count = len(line) - len(stripped)
        result.append(to_chars * indent_count + stripped)
    return "\n".join(result)
```

## Markdown to HTML Conversion

### Core Transformations
Process Markdown elements in priority order to avoid conflicts:
1. Code blocks (fenced and indented) -- protect from further transformation.
2. Headings (`#` through `######`).
3. Block quotes (`>`).
4. Lists (ordered and unordered).
5. Horizontal rules (`---`, `***`, `___`).
6. Paragraphs (consecutive non-blank lines).
7. Inline elements: bold, italic, code, links, images.

```python
import re

def markdown_heading_to_html(line):
    """Convert a Markdown heading line to HTML."""
    match = re.match(r"^(#{1,6})\s+(.+)$", line)
    if match:
        level = len(match.group(1))
        text = match.group(2)
        return f"<h{level}>{text}</h{level}>"
    return None

def markdown_inline_to_html(text):
    """Convert inline Markdown formatting to HTML."""
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    text = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', text)
    text = re.sub(r"!\[(.+?)\]\((.+?)\)", r'<img alt="\1" src="\2">', text)
    return text
```

### HTML to Markdown Conversion
Reverse the process, handling nested tags carefully:
- `<h1>` through `<h6>` become `#` through `######`.
- `<strong>` / `<b>` become `**...**`.
- `<em>` / `<i>` become `*...*`.
- `<a href="url">text</a>` becomes `[text](url)`.
- `<ul>/<li>` becomes `- item` lists.
- `<ol>/<li>` becomes `1. item` lists.

## Template Rendering

### Variable Substitution
```python
import re

def render_template(template, variables):
    """Replace {{variable}} placeholders with values."""
    def replace(match):
        key = match.group(1).strip()
        return str(variables.get(key, match.group(0)))
    return re.sub(r"\{\{(.+?)\}\}", replace, template)
```

### Conditional Sections
```python
def process_conditionals(template, variables):
    """Handle {{#if var}}...{{/if}} blocks."""
    pattern = r"\{\{#if\s+(\w+)\}\}(.*?)\{\{/if\}\}"
    def replace(match):
        var_name = match.group(1)
        content = match.group(2)
        if variables.get(var_name):
            return content
        return ""
    return re.sub(pattern, replace, template, flags=re.DOTALL)
```

## Document Comparison

### Line-by-Line Diff
```python
import difflib

def compare_documents(text_a, text_b):
    """Generate a unified diff between two documents."""
    lines_a = text_a.splitlines(keepends=True)
    lines_b = text_b.splitlines(keepends=True)
    diff = difflib.unified_diff(lines_a, lines_b,
                                 fromfile="original", tofile="modified")
    return "".join(diff)
```

### Semantic Comparison
For content-aware comparison (ignoring formatting):
1. Normalize whitespace in both documents.
2. Split into sentences or paragraphs.
3. Use `difflib.SequenceMatcher` for similarity scoring.
4. Report added, removed, and modified sections.

```python
def similarity_ratio(text_a, text_b):
    """Calculate similarity between two texts (0.0 to 1.0)."""
    return difflib.SequenceMatcher(None, text_a, text_b).ratio()
```

### Change Classification
- **Addition**: Content present only in the new version.
- **Deletion**: Content present only in the old version.
- **Modification**: Content in both but with differences.
- **Move**: Content present in both but at different positions.

## Table of Contents Generation

### Algorithm
1. Scan the document for heading elements (Markdown `#` or HTML `<h1>`-`<h6>`).
2. Extract the heading level and text.
3. Generate a slug from the heading text for anchor links.
4. Build a nested list reflecting the heading hierarchy.

```python
import re

def generate_toc(markdown_text):
    """Generate a Markdown table of contents from headings."""
    toc_lines = []
    for line in markdown_text.split("\n"):
        match = re.match(r"^(#{1,6})\s+(.+)$", line)
        if match:
            level = len(match.group(1))
            text = match.group(2)
            slug = slugify(text)
            indent = "  " * (level - 1)
            toc_lines.append(f"{indent}- [{text}](#{slug})")
    return "\n".join(toc_lines)

def slugify(text):
    """Convert heading text to a URL-friendly anchor."""
    slug = text.lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s]+", "-", slug)
    return slug.strip("-")
```

### Handling Edge Cases
- Duplicate headings: append a numeric suffix to the slug (`-1`, `-2`).
- Inline formatting in headings: strip bold/italic markers before slugifying.
- Skip headings inside code blocks.

## Best Practices
- Always preserve the original document; write transformations to a new file.
- When converting between formats, validate the output renders correctly.
- Handle encoding detection (UTF-8, Latin-1) before processing text.
- For large documents, process line by line or in chunks for memory efficiency.
- Use established libraries (markdown, beautifulsoup4) for production-grade
  conversions; hand-rolled regex is suitable for simple cases only.
- When generating TOC, provide an option to limit depth (e.g., only h1-h3).
- Test template rendering with edge cases: missing variables, empty lists,
  special characters in values.
