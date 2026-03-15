# Data Transformation Patterns

## CSV Processing
- Always use `csv.DictReader` and `csv.DictWriter` for header-aware operations
- Handle BOM markers with `encoding='utf-8-sig'`
- For large files, process row-by-row to avoid memory issues

## JSON Operations
- Use `json.dumps(data, indent=2, ensure_ascii=False)` for readable output
- Parse nested structures with recursive traversal
- Use `defaultdict` for aggregation tasks

## File Format Detection
- Check file extension and first few bytes for format identification
- Common patterns: CSV (comma-separated), TSV (tab-separated), JSON (starts with { or [)
- Handle mixed line endings (\r\n, \n)

## Data Cleaning
- Strip whitespace from all string fields
- Normalize empty strings vs null values
- Deduplicate by creating composite keys from relevant fields
