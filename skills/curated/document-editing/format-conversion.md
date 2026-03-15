# Format Conversion Skill

## Purpose
Convert documents between formats while preserving structure, formatting, and semantic content.

## Capabilities
- Convert between Markdown, HTML, plain text, CSV, and JSON
- Preserve document structure (headings, lists, tables, code blocks)
- Handle character encoding issues (UTF-8, ASCII, Latin-1)
- Transform tabular data between formats (CSV, TSV, Markdown tables, JSON arrays)
- Apply consistent formatting rules during conversion

## Guidelines
- Validate output structure matches the target format specification
- Preserve all content — never silently drop data during conversion
- Handle edge cases: empty cells, special characters, nested structures
- When converting tables, maintain column alignment and header rows
- Use standard encoding (UTF-8) unless the target format requires otherwise
