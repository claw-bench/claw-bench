# Multi-Format Data Processing Skill

## Purpose
Process, convert, and synthesize data across multiple file formats.

## Supported Conversions

### Structured Data
- JSON <-> YAML: Preserve nested structures, comments become fields
- CSV <-> JSON: Array of objects with header row as keys
- TOML -> JSON: Direct mapping of tables to objects

### Code Analysis
- Extract docstrings, function signatures, class hierarchies
- Map import dependencies between modules
- Identify public API surface

### Schema Operations
- Diff two SQL schemas to produce migration statements
- Convert between DDL dialects (PostgreSQL, MySQL, SQLite)
- Preserve constraints, indexes, and foreign keys

### Data Merging
- Join datasets on common keys (inner, left, outer)
- Handle type mismatches (string "123" vs integer 123)
- Deduplicate merged records

## Best Practices
- Always validate output format matches specification
- Preserve data fidelity — no silent type coercions
- Handle missing/null values explicitly
